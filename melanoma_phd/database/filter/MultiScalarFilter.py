import functools
from typing import List, Tuple

import numpy as np
import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class MultiScalarFilter(BaseFilter):
    def __init__(self, name: str, variables: List[ScalarVariable]) -> None:
        super().__init__()
        self._name = name
        self._variables = variables

    @property
    def name(self) -> str:
        return self._name

    def filter(self, dataframe: pd.DataFrame, range: Tuple[int, int]) -> pd.DataFrame:
        series_list = [
            dataframe[variable.id].between(range[0], range[1]) for variable in self._variables
        ]
        series = functools.reduce(np.logical_or, series_list)
        return dataframe[series]

    def range(self) -> Tuple[int, int]:
        left_range = [variable.range[0] for variable in self._variables if variable.range]
        right_range = [variable.range[1] for variable in self._variables if variable.range]
        return (min(left_range), max(right_range))
