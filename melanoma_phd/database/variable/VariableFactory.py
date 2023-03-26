from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Type

import pandas as pd
from pandas.core.dtypes.common import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_datetime64tz_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableType
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable, BooleanVariableConfig
from melanoma_phd.database.variable.CategoricalVariable import (
    CategoricalVariable,
    CategoricalVariableConfig,
)
from melanoma_phd.database.variable.DateTimeVariable import DateTimeVariable, DateTimeVariableConfig
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable, ScalarVariableConfig
from melanoma_phd.database.variable.SurvivalVariable import SurvivalVariable, SurvivalVariableConfig


@dataclass
class VariableFactoryClass:
    class_type: Type[BaseVariable]
    config_type: Type[BaseVariableConfig]


class VariableFactory:
    def __init__(self) -> None:
        self._static_classes: Dict[str, VariableFactoryClass] = {
            VariableType.SCALAR.value: VariableFactoryClass(
                class_type=ScalarVariable, config_type=ScalarVariableConfig
            ),
            VariableType.CATEGORICAL.value: VariableFactoryClass(
                class_type=CategoricalVariable, config_type=CategoricalVariableConfig
            ),
            VariableType.BOOLEAN.value: VariableFactoryClass(
                class_type=BooleanVariable, config_type=BooleanVariableConfig
            ),
            VariableType.DATETIME.value: VariableFactoryClass(
                class_type=DateTimeVariable, config_type=DateTimeVariableConfig
            ),
        }
        # So far, use a known set of dyanmic variables to create
        dynamic_classes = [
            VariableFactoryClass(class_type=SurvivalVariable, config_type=SurvivalVariableConfig)
        ]
        self._dynamic_classes: Dict[str, VariableFactoryClass] = {}
        for factory_class in dynamic_classes:
            self._dynamic_classes[factory_class.class_type.__name__] = factory_class

    def create(self, dataframe: pd.DataFrame, type: str, **kwargs) -> BaseVariable:
        if type in self._static_classes:
            factory_class = self._static_classes[type]
            new_variable = factory_class.class_type(config=factory_class.config_type(**kwargs))
            new_variable.init_from_dataframe(dataframe)
            return new_variable
        else:
            raise NameError(f"'{type}' variable type not supported!")

    def create_from_config(
        self, dataframe: pd.DataFrame, type: str, config: BaseVariableConfig
    ) -> BaseVariable:
        if type in self._static_classes:
            factory_class = self._static_classes[type]
            new_variable = factory_class.class_type(config=config)
            new_variable.init_from_dataframe(dataframe)
            return new_variable
        else:
            raise NameError(f"'{type}' variable type not supported!")

    def create_dynamic(
        self,
        dataframe: pd.DataFrame,
        type: str,
        **kwargs,
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        if type in self._dynamic_classes:
            factory_class = self._dynamic_classes[type]
            new_variable = factory_class.class_type(factory_class.config_type(**kwargs))
            new_variable.init_from_dataframe(dataframe)
            series = new_variable.create_new_series(dataframe)
            if series is not None:
                dataframe[new_variable.id] = series
            return new_variable, dataframe
        else:
            raise NameError(f"'{type}' dynamic variable class name not found!")

    def create_from_series(self, dataframe: pd.DataFrame, id: str) -> Optional[BaseVariable]:
        series = dataframe[id]
        create_boolean = lambda dataframe, id: self.create_from_config(
            dataframe=dataframe,
            type=VariableType.BOOLEAN.value,
            config=BooleanVariableConfig(
                id=id, name=id, selectable=True, categories={0: "No", 1: "Sí"}
            ),
        )
        if is_datetime64_any_dtype(series) or is_datetime64tz_dtype(series):
            return self.create_from_config(
                dataframe=dataframe,
                type=VariableType.DATETIME.value,
                config=DateTimeVariableConfig(id=id, name=id, selectable=True),
            )
        elif is_float_dtype(series) or is_integer_dtype(series):
            if set(series.dropna().unique()) == set([0, 1]):
                return create_boolean(
                    dataframe=dataframe,
                    id=id,
                )
            else:
                return self.create_from_config(
                    dataframe=dataframe,
                    type=VariableType.SCALAR.value,
                    config=ScalarVariableConfig(id=id, name=id, selectable=True),
                )
        elif is_string_dtype(series):
            return self.create_from_config(
                dataframe=dataframe,
                type=VariableType.CATEGORICAL.value,
                config=CategoricalVariableConfig(id=id, name=id, selectable=True),
            )
        elif is_bool_dtype(series):
            return create_boolean(
                dataframe=dataframe,
                id=id,
            )
        return None
