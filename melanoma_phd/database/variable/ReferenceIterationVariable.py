from typing import List

import pandas as pd

from melanoma_phd.database.variable.BaseIterationVariable import (
    BaseIterationVariable,
    BaseIterationVariableConfig,
)


class ReferenceIterationVariableConfig(BaseIterationVariableConfig):
    pass


class ReferenceIterationVariable(BaseIterationVariable):
    def __init__(self, config: ReferenceIterationVariableConfig) -> None:
        super().__init__(config=config)
        self._iterated_variables = config.iterated_variables

    def get_filter_dataframe(
        self, dataframe: pd.DataFrame, intervals: List[pd.Interval]
    ) -> pd.DataFrame:
        filter_dataframe = dataframe.loc[:, [variable.id for variable in self._iterated_variables]]
        filters = [
            filter_dataframe.applymap(lambda value: value in interval).any(axis=1)
            for interval in intervals
        ]
        filter = pd.concat(filters, axis=1).all(axis=1)
        filter_dataframe.loc[filter, :] = filter_dataframe.loc[filter, :].applymap(
            lambda value: any(value in interval for interval in intervals)
        )
        filter_dataframe.loc[~filter, :] = False
        return filter_dataframe
