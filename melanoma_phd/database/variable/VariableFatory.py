from typing import Tuple

import pandas as pd
from pandas.core.dtypes.common import is_float_dtype, is_integer_dtype

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableType
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.SurvivalVariable import SurvivalVariable


class VariableFactory:
    def __init__(self) -> None:
        self._static_classes = {
            VariableType.SCALAR.value: ScalarVariable,
            VariableType.CATEGORICAL.value: CategoricalVariable,
            VariableType.BOOLEAN.value: BooleanVariable,
        }
        # So far, use a known set of dyanmic variables to create
        dynamic_classes = [SurvivalVariable]
        self._dynamic_classes = {}
        for dynamic_class in dynamic_classes:
            self._dynamic_classes[dynamic_class.__name__] = dynamic_class

    def create(
        self, dataframe: pd.DataFrame, id: str, name: str, type: str, **kwargs
    ) -> BaseVariable:
        if type in self._static_classes:
            new_variable = self._static_classes[type](id=id, name=name, **kwargs)
            new_variable.init_from_dataframe(dataframe)
            return new_variable
        else:
            raise NameError(f"'{type}' variable type not supported!")

    def create_dynamic(
        self, class_name: str, dataframe: pd.DataFrame, id: str, name: str, type: str, **kwargs
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        if class_name in self._dynamic_classes:
            new_variable = self._dynamic_classes[class_name](id=id, name=name, **kwargs)
            assert isinstance(new_variable, self._static_classes[type])
            dataframe[new_variable.id] = new_variable.create_new_series(dataframe)
            new_variable.init_from_dataframe(dataframe)
            return new_variable, dataframe
        else:
            raise NameError(f"'{class_name}' dynamic variable class name not found!")

    def create_from_series(self, dataframe: pd.DataFrame, id: str) -> BaseVariable:
        series = dataframe[id]
        if is_float_dtype(series) or is_integer_dtype(series):
            return self.create(dataframe=dataframe, id=id, name=id, type=VariableType.SCALAR.value)
        # TODO: Support other types
