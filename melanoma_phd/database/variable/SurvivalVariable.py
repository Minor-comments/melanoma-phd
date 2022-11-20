import pandas as pd

from melanoma_phd.database.variable.BaseDynamicVariable import BaseDynamicVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class SurvivalVariable(ScalarVariable, BaseDynamicVariable):
    def __init__(
        self, id: str, name: str, duration_variable_id: str, events_variable_id: str
    ) -> None:
        super().__init__(id=id, name=name)
        self._duration_variable_id = duration_variable_id
        self._events_variable_id = events_variable_id

    def add_variable_to_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        # TODO: Add new column survival
        # https://towardsdatascience.com/kaplan-meier-curve-explained-9c78a681faca
        dataframe[self.id] = 0
        return dataframe

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return super().descriptive_statistics(dataframe=dataframe)
