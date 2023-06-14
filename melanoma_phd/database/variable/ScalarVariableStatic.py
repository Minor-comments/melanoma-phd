import pandas as pd

from melanoma_phd.database.variable.ScalarVariable import ScalarVariable, ScalarVariableConfig
from melanoma_phd.database.variable.VariableStaticMixin import VariableStaticMixin


class ScalarVariableStatic(VariableStaticMixin, ScalarVariable):
    def __init__(self, config: ScalarVariableConfig) -> None:
        super().__init__(config=config)

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        return super().get_series(dataframe=dataframe)

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
