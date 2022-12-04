from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import pandas as pd


class VariableType(Enum):
    SCALAR = "scalar"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"


@dataclass
class BaseVariable(ABC):
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    @abstractmethod
    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        self._check_valid_id(dataframe)

    @abstractmethod
    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        if self.id not in dataframe.columns:
            raise ValueError(f"'{self.id}' not present in dataframe")
