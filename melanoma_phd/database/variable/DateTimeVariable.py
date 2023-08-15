from dataclasses import dataclass
from typing import Any, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableStatisticalType
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig


@dataclass
class DateTimeVariableConfig(BaseVariableConfig):
    pass


class DateTimeVariable(BaseVariable):
    def __init__(self, config: DateTimeVariableConfig) -> None:
        super().__init__(config=config)
        self._interval: Optional[pd.Interval] = None

    @staticmethod
    def statistical_type() -> VariableStatisticalType:
        return VariableStatisticalType.DATETIME

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

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        raise NotImplementedError(
            f"DateTime variable '{self.id}' has no format descriptive statistics implementation"
        )
