from typing import List

import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable


class CategoricalFilter(BaseFilter):
    def __init__(self, variable: CategoricalVariable) -> None:
        super().__init__()
        self._variable = variable

    @property
    def name(self) -> str:
        return self._variable.name

    def filter(self, dataframe: pd.DataFrame, options: List[str]) -> pd.DataFrame:
        return (
            dataframe[
                dataframe[self._variable.id].isin(self._variable.get_category_values(options))
            ]
            if options
            else dataframe
        )

    def options(self) -> List[str]:
        return self._variable.category_names
