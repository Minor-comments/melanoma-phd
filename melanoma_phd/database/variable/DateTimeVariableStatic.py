from typing import Optional

import pandas as pd

from melanoma_phd.database.variable.DateTimeVariable import DateTimeVariable, DateTimeVariableConfig
from melanoma_phd.database.variable.VariableStaticMixin import VariableStaticMixin


class DateTimeVariableStatic(VariableStaticMixin, DateTimeVariable):
    def __init__(self, config: DateTimeVariableConfig) -> None:
        super().__init__(config=config)
        self._interval: Optional[pd.Interval] = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = self.get_series(dataframe=dataframe).dropna()
        self._interval = (
            pd.Interval(left=series.min(), right=series.max(), closed="both")
            if not series.empty
            else None
        )

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        return super().get_series(dataframe=dataframe)

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
