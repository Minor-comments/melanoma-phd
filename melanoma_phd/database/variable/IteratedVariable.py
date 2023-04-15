from dataclasses import dataclass

import pandas as pd

from melanoma_phd.database.variable.ScalarVariable import ScalarVariable, ScalarVariableConfig


@dataclass
class IteratedVariableConfig(ScalarVariableConfig):
    pass


class IteratedVariable(ScalarVariable):
    def __init__(self, config: IteratedVariableConfig) -> None:
        super().__init__(config=config)

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
