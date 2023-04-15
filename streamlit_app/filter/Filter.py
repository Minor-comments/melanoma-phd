from typing import Protocol

import pandas as pd


class Filter(Protocol):
    def select(self) -> None:
        pass

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass
