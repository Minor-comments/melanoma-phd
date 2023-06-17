from __future__ import annotations

from typing import Any, List, Optional, Protocol, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig

PValueType = float


class Variable(Protocol):
    """Protocol for all variables."""

    id: str
    name: str
    selectable: bool
    unique_id: Optional[str]

    def __init__(self, config: BaseVariableConfig) -> None:
        ...

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        ...

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        ...

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[Variable, List[Variable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        ...

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        ...

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        ...
