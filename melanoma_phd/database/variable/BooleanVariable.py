from dataclasses import dataclass
from typing import Dict, Optional, Union

from melanoma_phd.database.variable.CategoricalVariable import (
    CategoricalVariable,
    CategoricalVariableConfig,
)


@dataclass
class BooleanVariableConfig(CategoricalVariableConfig):
    pass


class BooleanVariable(CategoricalVariable):
    def __init__(
        self,
        config: BooleanVariableConfig,
    ) -> None:
        if not config.categories:
            config.categories = {0: "No", 1: "Yes"}
        super().__init__(config=config)
