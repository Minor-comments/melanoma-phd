from typing import Tuple

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class ScalarVariable(BaseVariable):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id, name=name)
        self._range = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = dataframe[self.id].dropna().astype(int)
        self._range = tuple([int(series.min()), int(series.max())]) if not series.empty else None

    @property
    def range(self) -> Tuple[int, int]:
        return self._range

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        series = dataframe[self.id].dropna()
        median = series.median()
        mean = series.mean()
        std_deviation = series.std()
        min = series.min()
        max = series.max()
        return pd.DataFrame(
            data={"median": median, "mean": mean, "std": std_deviation, "min": min, "max": max},
            index=[0],
        )

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
