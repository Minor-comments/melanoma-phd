from abc import ABC, abstractmethod

import pandas as pd


class BaseDynamicVariable(ABC):
    """Class for defining just the dynamic variable interface that must be inherited by new child classes in conjunction with a static variable class.
    NOTE: This class do not inherit from `BaseClass` in order to avoid diamond inheritance problem.
    """

    @abstractmethod
    def create_new_series(self, dataframe: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        if self.id in dataframe.columns:
            raise ValueError(f"'{self.id}' dynamic varible id already present in dataframe")
