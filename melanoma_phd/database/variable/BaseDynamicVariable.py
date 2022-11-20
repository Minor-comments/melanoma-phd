from abc import abstractmethod

import pandas as pd


class BaseDynamicVariable:
    """Class for defining just the dynamic variable interface that must be inherited by new child classes in conjunction with a static variable class.
    NOTE: This class do not inherit from `BaseClass` in order to avoid diamond inheritance problem.
    """

    @abstractmethod
    def add_variable_to_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass
