from typing import Dict

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class LaTeXArray:
    def __init__(self, variables_statistics: Dict[BaseVariable, pd.DataFrame]) -> None:
        self._variables = variables_statistics

    def __dump_variable(self, variable: BaseVariable, statistics: pd.DataFrame) -> str:
        """The array row as string from variable in LaTex syntax"""
        name = variable.name + " [" + " ".join(list(statistics.columns)) + "]"
        name = self.__convert_special_chars(name)
        row = r"\text{" + name + r"}"
        if isinstance(variable, ScalarVariable):
            row = (
                row
                + " & & "
                + r"\text{"
                + " ".join(
                    str(round(value, 2) if isinstance(value, float) else value)
                    for value in statistics.iloc[0, :]
                )
                + r"}"
                + r"\\ \hline"
            )
        elif isinstance(variable, CategoricalVariable):
            row = (
                row
                + " & "
                + r"\text{"
                + statistics.index[0]
                + r"}"
                + " & "
                + r"\text{"
                + " ".join(
                    str(round(value, 2) if isinstance(value, float) else value)
                    for value in statistics.iloc[0, :]
                    if value
                )
                + r"} \\"
            )
            for i in range(1, len(statistics.index)):
                row = (
                    row
                    + "& "
                    + r"\text{"
                    + statistics.index[i]
                    + r"}"
                    + " & "
                    + r"\text{"
                    + " ".join(
                        str(round(value, 2) if isinstance(value, float) else value)
                        for value in statistics.iloc[i, :]
                        if value
                    )
                    + r"} \\"
                )
            row = row + r" \hline"
        return row

    def dumps(self) -> str:
        """The array as string in LaTex syntax"""
        return (
            r"\begin{array}{|llc|} \hline"
            + "\n"
            + "\n".join(
                [
                    self.__dump_variable(variable, dataframe)
                    for variable, dataframe in self._variables.items()
                ]
            )
            + r"""
                \end{array}
                """
        )

    def __convert_special_chars(self, name: str) -> str:
        special_chars = {
            "\\": "\\textbackslash",
            "&": "\&",
            "%": "\%",
            "$": "\$",
            "#": "\#",
            "_": "\_",
            "{": "\{",
            "}": "\}",
            "~": "\\textasciitilde",
            "^": "\\textasciicircum",
        }
        for special_char, conversion in special_chars.items():
            name = name.replace(special_char, conversion)
        return name
