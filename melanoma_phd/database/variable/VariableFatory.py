from typing import Dict, Optional, Tuple, Type

import pandas as pd
from pandas.core.dtypes.common import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)
from melanoma_phd.database.variable.BaseDynamicVariable import (
    BaseDynamicVariable,
)

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableType
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.SurvivalVariable import SurvivalVariable


class VariableFactory:
    def __init__(self) -> None:
        self._static_classes: Dict[str, Type[BaseVariable]] = {
            VariableType.SCALAR.value: ScalarVariable,
            VariableType.CATEGORICAL.value: CategoricalVariable,
            VariableType.BOOLEAN.value: BooleanVariable,
        }
        # So far, use a known set of dyanmic variables to create
        dynamic_classes = [SurvivalVariable]
        self._dynamic_classes: Dict[str, Type[BaseDynamicVariable]] = {}
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
        self,
        class_name: str,
        dataframe: pd.DataFrame,
        id: str,
        name: str,
        type: str,
        **kwargs,
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        if class_name in self._dynamic_classes:
            new_variable = self._dynamic_classes[class_name](id=id, name=name, **kwargs)
            new_variable.init_from_dataframe(dataframe)
            series = new_variable.create_new_series(dataframe)
            if series is not None:
                dataframe[new_variable.id] = series
            return new_variable, dataframe
        else:
            raise NameError(f"'{class_name}' dynamic variable class name not found!")

    def create_from_series(
        self, dataframe: pd.DataFrame, id: str
    ) -> Optional[BaseVariable]:
        series = dataframe[id]
        create_boolean = lambda dataframe, id: self.create(
            dataframe=dataframe,
            id=id,
            name=id,
            type=VariableType.BOOLEAN.value,
            categories={0: "No", 1: "Sí"},
        )
        if is_float_dtype(series) or is_integer_dtype(series):
            if set(series.dropna().unique()) == set([0, 1]):
                return create_boolean(
                    dataframe=dataframe,
                    id=id,
                )
            else:
                return self.create(
                    dataframe=dataframe, id=id, name=id, type=VariableType.SCALAR.value
                )
        elif is_string_dtype(series):
            unique_values = list(series.dropna().unique())
            categories = dict(zip(unique_values, unique_values))
            return self.create(
                dataframe=dataframe,
                id=id,
                name=id,
                type=VariableType.CATEGORICAL.value,
                categories=categories,
            )
        elif is_bool_dtype(series):
            return create_boolean(
                dataframe=dataframe,
                id=id,
            )
