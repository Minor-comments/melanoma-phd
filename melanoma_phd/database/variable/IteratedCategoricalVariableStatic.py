from dataclasses import dataclass

import pandas as pd

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariableConfig
from melanoma_phd.database.variable.CategoricalVariableStatic import CategoricalVariableStatic


@dataclass
class IteratedCategoricalVariableConfig(CategoricalVariableConfig):
    pass


class IteratedCategoricalVariableStatic(CategoricalVariableStatic):
    def __init__(self, config: IteratedCategoricalVariableConfig) -> None:
        super().__init__(config=config)

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
