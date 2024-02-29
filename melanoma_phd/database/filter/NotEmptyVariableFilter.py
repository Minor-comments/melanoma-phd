import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.variable.BaseVariable import BaseVariable


class NotEmptyVariableFilter(BaseFilter):
    def __init__(self, variable: BaseVariable) -> None:
        super().__init__()
        self._variable = variable

    @property
    def name(self) -> str:
        return self._variable.name

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe[~dataframe[self._variable.id].isna()]
