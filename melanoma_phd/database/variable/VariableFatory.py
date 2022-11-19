from typing import Dict

import pandas as pd

from melanoma_phd.database.variable.Variable import (
    BaseVariable,
    CategoricalVariable,
    ScalarVarible,
    VariableType,
)


class VariableFactory:
    def create(self, id: str, name: str, type: str, **kwargs) -> Dict[str, BaseVariable]:
        match type:
            case VariableType.SCALAR.value:
                return ScalarVarible(id=id, name=name)
            case VariableType.CATEGORICAL.value:
                return CategoricalVariable(
                    id=id, name=name, category_name_values=kwargs["categories"]
                )

    def create_from_series(self, series: pd.Series) -> BaseVariable:
        raise NotImplementedError
