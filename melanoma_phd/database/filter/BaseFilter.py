from abc import ABC, abstractmethod, abstractproperty
from typing import Any

import pandas as pd


class BaseFilter(ABC):
    @abstractproperty
    def name(self) -> str:
        pass

    @abstractmethod
    def filter(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        pass
