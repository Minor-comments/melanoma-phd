from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

import pandas as pd

from melanoma_phd.database.Patient import Patient
from melanoma_phd.database.variable.BaseVariable import BaseVariable


class AbstractPatientDatabaseView(ABC):
    def __init__(self) -> None:
        pass

    @property
    @abstractmethod
    def dataframe(self) -> pd.DataFrame:
        pass

    @property
    @abstractmethod
    def variables(self) -> List[BaseVariable]:
        pass

    @property
    def index_variable(self) -> BaseVariable:
        for variable in self.variables:
            if variable.id == self.dataframe.index.name:
                return variable
        raise ValueError(f"No variable index found!")

    @property
    def patient_ids(self) -> List[int]:
        return list(self.dataframe.index.values)

    def get_patient(self, patient_id: int) -> Patient:
        return Patient(patient_id, self.dataframe.loc[patient_id])

    def get_patients(self, patient_ids: Optional[List[int]]) -> List[Patient]:
        if patient_ids:
            return [self.get_patient(patient_id) for patient_id in patient_ids]
        else:
            return [
                Patient(int(index), row) for index, row in self.dataframe.iterrows()
            ]

    def get_variable(self, variable_id: str) -> BaseVariable:
        for variable in self.variables:
            if variable.id == variable_id:
                return variable
        raise ValueError(f"'{variable_id}' variable identifier not found!")

    def get_variables(self, variable_ids: List[str]) -> List[BaseVariable]:
        return [self.get_variable(variable_id) for variable_id in variable_ids]

    def get_variables_by_type(
        self, types: Union[Type[BaseVariable], List[Type[BaseVariable]]]
    ) -> List[BaseVariable]:
        if not types:
            return self.variables
        elif types and isinstance(types, Type):
            types = [types]
        return [
            variable
            for variable in self.variables
            if any([isinstance(variable, variable_type) for variable_type in types])
        ]
