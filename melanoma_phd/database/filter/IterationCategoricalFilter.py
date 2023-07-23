from typing import List

import pandas as pd

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.variable.IterationCategoricalVariable import IterationCategoricalVariable


class IterationCategoricalFilter(CategoricalFilter):
    def __init__(
        self,
        name: str,
        reference_variable: IterationCategoricalVariable,
        iteration_variables: List[IterationCategoricalVariable],
    ) -> None:
        super().__init__(variable=reference_variable)
        self._name = name
        self._reference_variable = reference_variable
        self._iteration_variables = iteration_variables

    @property
    def name(self) -> str:
        return self._name

    def filter(self, dataframe: pd.DataFrame, options: List[str]) -> pd.DataFrame:
        if not options:
            return dataframe

        filter_dataframe = self._reference_variable.get_filter_dataframe(
            dataframe=dataframe, category_options=options
        )
        mask_series = filter_dataframe.any(skipna=True, axis=1)
        dataframe = dataframe.loc[mask_series]
        filter_dataframe = filter_dataframe.loc[mask_series]
        for iteration_variable in self._iteration_variables:
            dataframe = iteration_variable.filter(
                dataframe=dataframe, filter_dataframe=filter_dataframe
            )
        return dataframe
