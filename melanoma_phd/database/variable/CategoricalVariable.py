from typing import Dict, List, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class CategoricalVariable(BaseVariable):
    def __init__(self, id: str, name: str, categories: Dict[Union[int, str], str]) -> None:
        super().__init__(id=id, name=name)
        self._categories = categories

    @property
    def category_names(self) -> List[str]:
        return self._categories.values()

    @property
    def category_values(self) -> List[str]:
        return self._categories.keys()

    def get_category_name(self, value: Union[int, float, str]) -> str:
        return self._categories.get(value, str(value))

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        series = dataframe[self.id].map(self._categories)
        counts = series.value_counts()
        percent = series.value_counts(normalize=True)
        percent100 = percent.mul(100).round(1).astype(str) + "%"
        return pd.DataFrame({"counts": counts, "per": percent, "per100": percent100})
