from dataclasses import dataclass
from typing import Any, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig


@dataclass
class DateTimeVariableConfig(BaseVariableConfig):
    pass


class DateTimeVariable(BaseVariable):
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

    @property
    def interval(self) -> pd.Interval:
        if self._interval:
            return self._interval
        raise ValueError(f"interval not defined in datetime variable '{self.id}'")

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        raise NotImplementedError(
            f"DateTime variable '{self.id}' has no descriptive statistics implementation"
        )

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
