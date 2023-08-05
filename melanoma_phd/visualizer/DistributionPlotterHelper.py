from typing import List, Optional

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.RemainingDistributionVariable import (
    RemainingDistributionVariable,
)
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class DistributionPlotterHelper:
    def __init__(self, distribution_variables: List[ScalarVariable]) -> None:
        self._distribution_variables = distribution_variables

    def generate_title(self, categorical_variable: Optional[CategoricalVariable] = None) -> str:
        has_others = any(
            variable.name == RemainingDistributionVariable.DEFAULT_NAME
            for variable in self._distribution_variables
        )
        distribution_variable_names = sorted(
            [
                variable.name
                for variable in self._distribution_variables
                if variable.name != RemainingDistributionVariable.DEFAULT_NAME
            ]
        )
        if has_others:
            distribution_variable_names.append(RemainingDistributionVariable.DEFAULT_NAME)

        title = f"Distribution of {' / '.join(distribution_variable_names)}"

        if categorical_variable:
            title += f" over {categorical_variable.name}"

        return title

    def generate_variable_name_with_n_size(self, variable_index: int, n: int) -> str:
        if len(self._distribution_variables) == 1:
            return f"N = {n}"
        else:
            return f"{self._distribution_variables[variable_index].name}<br>N = {n}"
