from dataclasses import dataclass
from typing import List

import pandas as pd

from melanoma_phd.database.variable.ScalarVariable import ScalarVariable, ScalarVariableConfig


@dataclass
class RemainingDistributionVariableConfig(ScalarVariableConfig):
    distribution_variables: List[ScalarVariable]
    total_distribution_sum: int = 100


class RemainingDistributionVariable(ScalarVariable):
    DEFAULT_NAME = "Others"

    def __init__(self, config: RemainingDistributionVariableConfig) -> None:
        super().__init__(config=config)
        self._distribution_variables = config.distribution_variables
        self._total_distribution_sum = config.total_distribution_sum

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        df = pd.DataFrame(
            [
                variable.get_series(dataframe)
                for variable in self._distribution_variables
                if variable.id != self.id
            ],
        ).T
        df[self.name] = self._total_distribution_sum - df.sum(axis=1)
        return df[self.name]

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        for variable in self._distribution_variables:
            variable._check_valid_id(dataframe)
