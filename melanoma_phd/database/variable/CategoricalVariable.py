from typing import Dict, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class CategoricalVariable(BaseVariable):
    def __init__(
        self, id: str, name: str, categories: Dict[Union[int, str], str]
    ) -> None:
        super().__init__(id=id, name=name)
        self._categories = categories

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    @property
    def category_names(self) -> List[str]:
        return self._categories.values()

    @property
    def category_values(self) -> List[str]:
        return self._categories.keys()

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
        group_by_id: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:
        series = dataframe[self.id].map(self._categories)
        if group_by_id is None:
            counts = series.value_counts()
        else:
            new_column = f"_tmp_{self.id}"
            assert new_column not in dataframe.columns

            group_by_ids = (
                [group_by_id] if isinstance(group_by_id, str) else group_by_id
            )
            new_dataframe = dataframe[group_by_ids].copy()
            new_dataframe[new_column] = dataframe[self.id].map(self._categories)
            counts = (
                new_dataframe.groupby(group_by_ids + [new_column])[new_column]
                .size()
                .unstack(fill_value=0)
                .stack()
            )
        percent = series.value_counts(normalize=True)
        percent100 = percent.mul(100).round(1)
        return pd.DataFrame({"n": counts, "%": percent100})

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
