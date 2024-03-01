from copy import deepcopy
from dataclasses import dataclass
from typing import Any, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import (
    BaseVariable,
    VariableStatisticalType,
)
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig


@dataclass
class StringVariableConfig(BaseVariableConfig):
    pass


class StringVariable(BaseVariable):
    def __init__(self, config: StringVariableConfig) -> None:
        super().__init__(config=config)

    @staticmethod
    def statistical_type() -> VariableStatisticalType:
        return VariableStatisticalType.NONE

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        return deepcopy(dataframe[self.id])

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        raise NotImplementedError(
            f"Descriptive statistics is not implemented on {self.__class__.__name__}"
        )

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        raise NotImplementedError(
            f"Format descriptive statistics is not implemented on {self.__class__.__name__}"
        )

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
