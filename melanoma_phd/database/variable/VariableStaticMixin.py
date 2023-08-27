from __future__ import annotations

from copy import deepcopy

import pandas as pd

from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.Variable import Variable


class VariableStaticMixin:
    """Mixin class for all static variables."""

    def __init__(self, config: BaseVariableConfig) -> None:
        super().__init__(config=config)

    def get_series(self: Variable, dataframe: pd.DataFrame) -> pd.Series:
        return deepcopy(dataframe[self.id])

    def _check_valid_id(self: Variable, dataframe: pd.DataFrame) -> None:
        if self.id not in dataframe.columns and self.id != dataframe.index.name:
            raise ValueError(f"'{self.id}' not present in dataframe")
