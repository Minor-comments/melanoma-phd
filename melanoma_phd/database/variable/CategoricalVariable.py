from typing import Dict, List, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class CategoricalVariable(BaseVariable):
    def __init__(self, id: str, name: str, categories: Dict[Union[int, str], str]) -> None:
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

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        series = dataframe[self.id].map(self._categories)
        counts = series.value_counts()
        percent = series.value_counts(normalize=True)
        percent100 = percent.mul(100).round(1)
        return pd.DataFrame({"n": counts, "%": percent100})

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
