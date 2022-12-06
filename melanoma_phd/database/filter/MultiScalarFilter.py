import functools
from typing import List

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

    def filter(self, dataframe: pd.DataFrame, intervals: List[pd.Interval]) -> pd.DataFrame:
        if not intervals:
            return dataframe
        series_list = [
            dataframe[variable.id].map(
                lambda value: any([value in interval for interval in intervals])
            )
            for variable in self._variables
        ]
        series = functools.reduce(np.logical_or, series_list)
        return dataframe[series]

    def interval(self) -> pd.Interval:
        left_interval = [variable.interval[0] for variable in self._variables if variable.interval]
        right_interval = [variable.interval[1] for variable in self._variables if variable.interval]
        return (min(left_interval), max(right_interval))
