from typing import List, Tuple

import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class ScalarFilter(BaseFilter):
    def __init__(self, variable: ScalarVariable) -> None:
        super().__init__()
        self._variable = variable

    @property
    def name(self) -> str:
        return self._variable.name

    def filter(self, dataframe: pd.DataFrame, range: Tuple[int, int]) -> pd.DataFrame:
        return dataframe[dataframe[self._variable.id].between(range[0], range[1])]

    def range(self) -> Tuple[int, int]:
        return self._variable.range
