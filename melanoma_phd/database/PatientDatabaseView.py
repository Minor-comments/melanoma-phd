from typing import List

import pandas as pd

from melanoma_phd.database.AbstractPatientDatabaseView import AbstractPatientDatabaseView
from melanoma_phd.database.variable.BaseVariable import BaseVariable


class PatientDatabaseView(AbstractPatientDatabaseView):
    def __init__(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> None:
        self._dataframe: pd.DataFrame = dataframe
        self._variables: List[BaseVariable] = variables

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def variables(self) -> List[BaseVariable]:
        return self._variables
