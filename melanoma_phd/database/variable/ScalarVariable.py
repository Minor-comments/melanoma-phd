import logging
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableStatisticalType
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.StatisticFieldName import StatisticFieldName


@dataclass
class ScalarVariableConfig(BaseVariableConfig):
    pass


class ScalarVariable(BaseVariable):
    def __init__(self, config: ScalarVariableConfig) -> None:
        super().__init__(config=config)
        self._interval: Optional[pd.Interval] = None

    @staticmethod
    def statistical_type() -> VariableStatisticalType:
        return VariableStatisticalType.SCALAR

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = self.get_series(dataframe=dataframe).dropna().astype(int)
        self._interval = (
            pd.Interval(left=series.min(), right=series.max(), closed="both")
            if not series.empty
            else None
        )

    @property
    def interval(self) -> pd.Interval:
        if self._interval:
            return self._interval
        raise ValueError(f"interval not defined in scalar variable '{self.id}'")

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        if not group_by:
            series = self.get_series(dataframe=dataframe).dropna()
            count = series.count()
            median = series.median()
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            mean = series.mean()
            std_deviation = series.std()
            min = series.min()
            max = series.max()
            return pd.DataFrame(
                data={
                    StatisticFieldName.COUNT.value: count,
                    StatisticFieldName.MEDIAN.value: median,
                    StatisticFieldName.MEAN.value: mean,
                    StatisticFieldName.STD_DEVIATION.value: std_deviation,
                    StatisticFieldName.MIN_VALUE.value: min,
                    StatisticFieldName.MAX_VALUE.value: max,
                    StatisticFieldName.QUARTILE_1.value: q1,
                    StatisticFieldName.QUARTILE_3.value: q3,
                },
                index=[0],
            )
        else:
            group_by_list = [group_by] if isinstance(group_by, BaseVariable) else group_by
            group_by_data = [
                group_by_variable.get_series(dataframe=dataframe)
                for group_by_variable in group_by_list
            ]
            result = dataframe.groupby(group_by_data)[self.id].agg(
                [
                    StatisticFieldName.MEDIAN.value,
                    StatisticFieldName.MEAN.value,
                    StatisticFieldName.STD_DEVIATION.value,
                    StatisticFieldName.MIN_VALUE.value,
                    StatisticFieldName.MAX_VALUE.value,
                    StatisticFieldName.QUARTILE_1.value,
                    StatisticFieldName.QUARTILE_3.value,
                ],
            )
            return result

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        row_name = f"{self.name}   mean ± std (min-max) median"
        value_name = ""
        value = (
            f"{dataframe.iloc[0][StatisticFieldName.MEAN.value]:.2f} ± {dataframe.iloc[0][StatisticFieldName.STD_DEVIATION.value]:.2f}"
            f" ({dataframe.iloc[0][StatisticFieldName.MIN_VALUE.value]:.2f}-{dataframe.iloc[0][StatisticFieldName.MAX_VALUE.value]:.2f})"
            f" {dataframe.iloc[0][StatisticFieldName.MEDIAN.value]:.2f}"
            f" ({dataframe.iloc[0][StatisticFieldName.QUARTILE_1.value]:.2f}-{dataframe.iloc[0][StatisticFieldName.QUARTILE_3.value]:.2f})"
        )
        return [[row_name, value_name, value]]

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)

    def get_data_by_categories(
        self,
        dataframe: pd.DataFrame,
        category_variable: CategoricalVariable,
        remove_nulls: bool = False,
        remove_short_categories: bool = False,
    ) -> Tuple[pd.Series, ...]:
        if remove_nulls:
            get_data = lambda variable: variable.get_non_na_series
        else:
            get_data = lambda variable: variable.get_series

        series = []
        removed_categories = []
        for category_name, data in dataframe.groupby(get_data(category_variable)(dataframe)):
            serie = get_data(self)(data)
            if remove_short_categories and len(serie) < 3:
                removed_categories.append(category_name)
            else:
                series.append(serie)
        if removed_categories:
            logging.warning(
                f"Removed `{self.name}` data corresponding to `{removed_categories}` categories of variable `{category_variable.name}` due to too few values in this category."
            )
        return tuple(series)
