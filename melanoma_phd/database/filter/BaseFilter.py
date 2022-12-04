from abc import ABC, abstractmethod, abstractproperty

import pandas as pd


class BaseFilter(ABC):
    @abstractproperty
    def name(self) -> str:
        pass

    @abstractmethod
    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass
