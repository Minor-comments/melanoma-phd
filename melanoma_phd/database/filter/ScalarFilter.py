import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class ScalarFilter(BaseFilter):
    def __init__(self, variable: ScalarVariable) -> None:
        super().__init__()
        self._variable = variable

    @property
    def name(self) -> str:
        return self._variable.name

    def filter(self, dataframe: pd.DataFrame, interval: pd.Interval) -> pd.DataFrame:
        return dataframe[dataframe[self._variable.id].map(lambda value: value in interval)]

    def interval(self) -> pd.Interval:
        return self._variable.interval
