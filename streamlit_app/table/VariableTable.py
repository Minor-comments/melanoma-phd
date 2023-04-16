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
        name = variable.name + " [" + " / ".join(list(statistics.columns)) + "]"
        rows = []
        for i in range(0, len(statistics.index)):
            row_values = [value for value in statistics.iloc[i, :] if value]
            row_name = name if i == 0 else ""
            value_name = statistics.index[i] if statistics.index[i] != 0 or i != 0 else ""
            row = [row_name, value_name, " / ".join([str(row_value) for row_value in row_values])]
            rows.append(row)
        return rows
