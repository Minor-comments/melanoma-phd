from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.StatisticFieldName import StatisticFieldName


@dataclass
class CategoricalVariableConfig(BaseVariableConfig):
    categories: Optional[Dict[Union[int, float, str], str]] = None


class CategoricalVariable(BaseVariable):
    def __init__(self, config: CategoricalVariableConfig) -> None:
        super().__init__(config=config)
        self._categories = config.categories

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        if not self._categories:
            series = super().get_series(dataframe=dataframe)
            unique_values = list(series.dropna().unique())
            self._categories = dict(zip(unique_values, unique_values))

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        series = super().get_series(dataframe=dataframe)
        categories_values = list(self._categories.keys())
        series_unique_values = list(series.dropna().unique())
        if not set(categories_values).issuperset(series_unique_values):
            raise ValueError(
                f"{series_unique_values} categories are not present in {categories_values} variable categories for `{self.id}`"
            )
        if type(categories_values[0]) != type(series_unique_values[0]):
            return series.dropna().astype(type(categories_values[0])).map(self._categories)
        return series.map(self._categories)

    def get_numeric_series(self, data: Union[pd.DataFrame, pd.Series]) -> pd.Series:
        if isinstance(data, pd.Series):
            series = data
        else:
            series = self.get_series(dataframe=data)
        return self.get_numeric(series=series)
    
    @classmethod
    def get_numeric(cls, series: pd.Series) -> pd.Series:
        if str(series.dtype) in ["object", "category"]:
            unique = series.unique()
            return series.map({value: i for i, value in enumerate(unique)}).astype(int)
        return series

    @property
    def category_names(self) -> List[str]:
        return list(self._categories.values())

    @property
    def category_values(self) -> List[str]:
        return [str(key) for key in self._categories.keys()]

    def get_category_name(self, value: Union[int, float, str]) -> str:
        return self._categories.get(value, str(value))

    def get_category_names(self, values: List[Union[int, float, str]]) -> List[str]:
        return [self.get_category_name(value) for value in values]

    def get_category_value(self, name: str) -> Union[int, float, str]:
        for category_value, category_name in self._categories.items():
            if category_name == name:
                return category_value
        raise ValueError(
            f"'{name}' category name not present in {self._categories} variable categories"
        )

    def get_category_values(self, names: List[str]) -> List[Union[int, float, str]]:
        return [self.get_category_value(name) for name in names]

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        series = self.get_series(dataframe=dataframe)
        if not group_by:
            counts = series.value_counts()
        else:
            new_column = f"_tmp_{self.id}"
            assert new_column not in dataframe.columns

            group_by_list = [group_by] if isinstance(group_by, BaseVariable) else group_by
            new_dataframe_data = {
                group_by_variable.id: group_by_variable.get_series(dataframe=dataframe)
                for group_by_variable in group_by_list
            }
            new_dataframe_data[new_column] = series
            new_dataframe = pd.DataFrame.from_dict(new_dataframe_data, orient="columns")
            group_by_ids = list(new_dataframe_data.keys())
            counts = cast(
                pd.Series,
                new_dataframe.groupby(group_by_ids)[new_column]
                .size()
                .unstack(fill_value=0)
                .stack(),
            )
        percent = series.value_counts(normalize=True)
        percent100 = percent.mul(100).round(1)
        return pd.DataFrame(
            {
                StatisticFieldName.COUNT.value: counts,
                StatisticFieldName.PERCENTAGE.value: percent100,
            }
        )

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        name = f"{self.name}   N (%)"
        rows: List[List[str]] = []
        for i in range(0, len(dataframe.index)):
            row_name = name if i == 0 else ""
            value_name = str(dataframe.index[i]) if dataframe.index[i] != 0 or i != 0 else ""
            row = [
                row_name,
                value_name,
                f"{dataframe.iloc[i][StatisticFieldName.COUNT.value]} ({dataframe.iloc[i][StatisticFieldName.PERCENTAGE.value]})",
            ]
            rows.append(row)
        return rows

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
