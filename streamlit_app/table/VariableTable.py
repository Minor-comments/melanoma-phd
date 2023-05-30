from typing import Any, Dict, List

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class VariableTable:
    def __init__(self, variables_statistics: Dict[BaseVariable, pd.DataFrame]) -> None:
        self._variables = variables_statistics

    def rows(self) -> List[List[List[Any]]]:
        return [
            self.__rows_variable(variable, dataframe)
            for variable, dataframe in self._variables.items()
        ]

    def __rows_variable(self, variable: BaseVariable, statistics: pd.DataFrame) -> List[List[Any]]:
        return variable.format_descriptive_statistics(dataframe=statistics)
