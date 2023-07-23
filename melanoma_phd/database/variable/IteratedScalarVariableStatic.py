from dataclasses import dataclass

import pandas as pd

from melanoma_phd.database.variable.ScalarVariable import ScalarVariableConfig
from melanoma_phd.database.variable.ScalarVariableStatic import ScalarVariableStatic


@dataclass
class IteratedScalarVariableConfig(ScalarVariableConfig):
    pass


class IteratedScalarVariableStatic(ScalarVariableStatic):
    def __init__(self, config: IteratedScalarVariableConfig) -> None:
        super().__init__(config=config)

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
