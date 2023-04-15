from typing import List

import numpy as np
import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.IterationVariable import IterationVariable
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable


class IterationFilter(BaseFilter):
    def __init__(
        self,
        name: str,
        reference_variable: ReferenceIterationVariable,
        iteration_variables: List[IterationVariable],
    ) -> None:
        super().__init__()
        self._name = name
        self._reference_variable = reference_variable
        self._iteration_variables = iteration_variables

    @property
    def name(self) -> str:
        return self._name

    def interval(self) -> pd.Interval:
        return self._reference_variable.interval

    def filter(self, dataframe: pd.DataFrame, interval: pd.Interval) -> pd.DataFrame:
        filter_dataframe = self._reference_variable.get_filter_dataframe(
            dataframe=dataframe, interval=interval
        )
        for iteration_variable in self._iteration_variables:
            dataframe = iteration_variable.filter(
                dataframe=dataframe, filter_dataframe=filter_dataframe
            )
        return dataframe
