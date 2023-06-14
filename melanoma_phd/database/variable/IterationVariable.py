from typing import List

from melanoma_phd.database.variable.BaseIterationVariable import (
    BaseIterationVariable,
    BaseIterationVariableConfig,
)
from melanoma_phd.database.variable.IteratedVariableStatic import IteratedVariableStatic
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable


class IterationVariableConfig(BaseIterationVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        reference_variable: ReferenceIterationVariable,
        iterated_variables: List[IteratedVariableStatic],
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
            iterated_variables=iterated_variables,
        )
        self.reference_variable = reference_variable


class IterationVariable(BaseIterationVariable):
    def __init__(self, config: IterationVariableConfig) -> None:
        super().__init__(config=config)
        self._reference_variable = config.reference_variable

    @property
    def reference_variable(self):
        return self._reference_variable
