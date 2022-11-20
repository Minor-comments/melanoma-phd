import pandas as pd

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

    def create(self, id: str, name: str, type: str, **kwargs) -> BaseVariable:
        if type in self._static_classes:
            return self._static_classes[type](id=id, name=name, **kwargs)
        else:
            raise NameError(f"'{type}' variable type not supported!")

    def create_dynamic(
        self, class_name: str, id: str, name: str, type: str, **kwargs
    ) -> BaseVariable:
        if class_name in self._dynamic_classes:
            new_variable = self._dynamic_classes[class_name](id=id, name=name, **kwargs)
            assert isinstance(new_variable, self._static_classes[type])
            return new_variable
        else:
            raise NameError(f"'{class_name}' dynamic variable class name not found!")

    def create_from_series(self, series: pd.Series) -> BaseVariable:
        raise NotImplementedError
