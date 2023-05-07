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

    def get_filter_dataframe(self, dataframe: pd.DataFrame, interval: pd.Interval) -> pd.DataFrame:
        filter_dataframe = dataframe.loc[:, [variable.id for variable in self._iterated_variables]]
        for column in filter_dataframe:
            filter_dataframe.loc[:, column] = dataframe[column].map(lambda value: value in interval)
        return filter_dataframe
