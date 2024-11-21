from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type, Union

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
from melanoma_phd.database.variable.BooleanVariableStatic import (
    BooleanVariableConfig,
    BooleanVariableStatic,
)
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariableConfig
from melanoma_phd.database.variable.CategoricalVariableStatic import (
    CategoricalVariableStatic,
)
from melanoma_phd.database.variable.DateTimeVariable import DateTimeVariableConfig
from melanoma_phd.database.variable.DateTimeVariableStatic import DateTimeVariableStatic
from melanoma_phd.database.variable.IteratedCategoricalVariableStatic import (
    IteratedCategoricalVariableConfig,
    IteratedCategoricalVariableStatic,
)
from melanoma_phd.database.variable.IteratedScalarVariableStatic import (
    IteratedScalarVariableConfig,
    IteratedScalarVariableStatic,
)
from melanoma_phd.database.variable.IterationCategoricalVariable import (
    IterationCategoricalVariable,
    IterationCategoricalVariableConfig,
)
from melanoma_phd.database.variable.IterationScalarVariable import (
    IterationScalarVariable,
    IterationScalarVariableConfig,
)
from melanoma_phd.database.variable.ReferenceIterationVariable import (
    ReferenceIterationVariable,
    ReferenceIterationVariableConfig,
)
from melanoma_phd.database.variable.ScalarVariable import ScalarVariableConfig
from melanoma_phd.database.variable.ScalarVariableStatic import ScalarVariableStatic
from melanoma_phd.database.variable.StringVariable import (
    StringVariable,
    StringVariableConfig,
)
from melanoma_phd.database.variable.SurvivalVariable import (
    SurvivalVariable,
    SurvivalVariableConfig,
)
from melanoma_phd.database.variable.VariableDynamicMixin import (
    BaseDynamicVariableConfig,
)


@dataclass
class VariableFactoryClass:
    class_type: Type[BaseVariable]
    config_type: Type[BaseVariableConfig]


class VariableFactory:
    def __init__(self) -> None:
        self._static_classes: Dict[str, VariableFactoryClass] = {
            VariableType.SCALAR.value: VariableFactoryClass(
                class_type=ScalarVariableStatic, config_type=ScalarVariableConfig
            ),
            VariableType.CATEGORICAL.value: VariableFactoryClass(
                class_type=CategoricalVariableStatic,
                config_type=CategoricalVariableConfig,
            ),
            VariableType.BOOLEAN.value: VariableFactoryClass(
                class_type=BooleanVariableStatic, config_type=BooleanVariableConfig
            ),
            VariableType.STRING.value: VariableFactoryClass(
                class_type=StringVariable, config_type=StringVariableConfig
            ),
            VariableType.DATETIME.value: VariableFactoryClass(
                class_type=DateTimeVariableStatic, config_type=DateTimeVariableConfig
            ),
            VariableType.ITERATED_SCALAR.value: VariableFactoryClass(
                class_type=IteratedScalarVariableStatic,
                config_type=IteratedScalarVariableConfig,
            ),
            VariableType.ITERATED_CATEGORICAL.value: VariableFactoryClass(
                class_type=IteratedCategoricalVariableStatic,
                config_type=IteratedCategoricalVariableConfig,
            ),
        }
        # So far, use a known set of dyanmic variables to create
        dynamic_classes = [
            VariableFactoryClass(
                class_type=ReferenceIterationVariable,
                config_type=ReferenceIterationVariableConfig,
            ),
            VariableFactoryClass(
                class_type=IterationScalarVariable,
                config_type=IterationScalarVariableConfig,
            ),
            VariableFactoryClass(
                class_type=IterationCategoricalVariable,
                config_type=IterationCategoricalVariableConfig,
            ),
            VariableFactoryClass(
                class_type=SurvivalVariable, config_type=SurvivalVariableConfig
            ),
        ]
        self._dynamic_classes: Dict[str, VariableFactoryClass] = {}
        for factory_class in dynamic_classes:
            self._dynamic_classes[factory_class.class_type.__name__] = factory_class

    def create(self, dataframe: pd.DataFrame, type: str, **kwargs) -> BaseVariable:
        if type in self._static_classes:
            factory_class = self._static_classes[type]
            new_variable = factory_class.class_type(
                config=factory_class.config_type(**kwargs)
            )
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

    def create_dynamic_from_config(
        self,
        dataframe: pd.DataFrame,
        type: str,
        config: BaseDynamicVariableConfig,
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        if type in self._dynamic_classes:
            factory_class = self._dynamic_classes[type]
            new_variable = factory_class.class_type(config=config)
            new_variable.init_from_dataframe(dataframe)
            series = new_variable.create_new_series(dataframe)
            if series is not None:
                dataframe[new_variable.id] = series
            return new_variable, dataframe
        else:
            raise NameError(f"'{type}' dynamic variable class name not found!")

    def create_reference_iteration(
        self,
        dataframe: pd.DataFrame,
        type: str,
        iterated_variables: List[IteratedScalarVariableStatic],
        **kwargs,
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        return self.create_dynamic(
            dataframe=dataframe,
            type=type,
            iterated_variables=iterated_variables,
            **kwargs,
        )

    def create_iteration(
        self,
        dataframe: pd.DataFrame,
        type: str,
        reference_variable: ReferenceIterationVariable,
        iterated_variables: List[
            Union[IteratedScalarVariableStatic, IteratedCategoricalVariableStatic]
        ],
        **kwargs,
    ) -> Tuple[BaseVariable, pd.DataFrame]:
        return self.create_dynamic(
            dataframe=dataframe,
            type=type,
            reference_variable=reference_variable,
            iterated_variables=iterated_variables,
            **kwargs,
        )

    def create_from_series(
        self, dataframe: pd.DataFrame, id: str
    ) -> Optional[BaseVariable]:
        series = dataframe[id]
        create_boolean = lambda dataframe, id: self.create_from_config(
            dataframe=dataframe,
            type=VariableType.BOOLEAN.value,
            config=BooleanVariableConfig(
                id=id, name=id, selectable=True, categories={0: "No", 1: "Sí"}
            ),
        )
        series_drop_na = series.dropna()
        if is_datetime64_any_dtype(series_drop_na) or is_datetime64tz_dtype(series_drop_na):
            return self.create_from_config(
                dataframe=dataframe,
                type=VariableType.DATETIME.value,
                config=DateTimeVariableConfig(id=id, name=id, selectable=True),
            )
        elif is_float_dtype(series_drop_na) or is_integer_dtype(series_drop_na):
            if set(series_drop_na.unique()) == set([0, 1]):
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
        elif is_string_dtype(series_drop_na):
            return self.create_from_config(
                dataframe=dataframe,
                type=VariableType.CATEGORICAL.value,
                config=CategoricalVariableConfig(id=id, name=id, selectable=True),
            )
        elif is_bool_dtype(series_drop_na):
            return create_boolean(
                dataframe=dataframe,
                id=id,
            )
        else:
            print(f"Error: Could not create a variable '{id}' from series with type {series.dtype}")
        return None
