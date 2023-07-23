import re
from typing import List

from melanoma_phd.database.variable.BaseIterationScalarVariable import (
    BaseIterationScalarVariable,
    BaseIterationScalarVariableConfig,
)
from melanoma_phd.database.variable.IteratedScalarVariableStatic import IteratedScalarVariableStatic
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable


class IterationScalarVariableConfig(BaseIterationScalarVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        reference_variable: ReferenceIterationVariable,
        iterated_variables: List[IteratedScalarVariableStatic],
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
            iterated_variables=iterated_variables,
        )
        self.reference_variable = reference_variable


class IterationScalarVariable(BaseIterationScalarVariable):
    def __init__(self, config: IterationScalarVariableConfig) -> None:
        super().__init__(config=config)
        self._reference_variable = config.reference_variable

    @property
    def reference_variable(self):
        return self._reference_variable

    @property
    def name_without_iteration(self) -> str:
        return re.sub(r" *\d+\.\.\d+ *", "", self.name)
