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
    id: str
    name: str

    @abstractmethod
    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass
