from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseFilter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def filter(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        pass
