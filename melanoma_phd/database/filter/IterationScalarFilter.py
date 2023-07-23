from typing import List

import numpy as np
import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.IterationScalarVariable import IterationScalarVariable
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable


class IterationScalarFilter(BaseFilter):
    def __init__(
        self,
        name: str,
        reference_variable: ReferenceIterationVariable,
        iteration_variables: List[IterationScalarVariable],
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

    def filter(self, dataframe: pd.DataFrame, intervals: List[pd.Interval]) -> pd.DataFrame:
        filter_dataframe = self._reference_variable.get_filter_dataframe(
            dataframe=dataframe, intervals=intervals
        )
        mask_series = filter_dataframe.any(skipna=True, axis=1)
        dataframe = dataframe.loc[mask_series]
        filter_dataframe = filter_dataframe.loc[mask_series]
        for iteration_variable in self._iteration_variables:
            dataframe = iteration_variable.filter(
                dataframe=dataframe, filter_dataframe=filter_dataframe
            )
        return dataframe
