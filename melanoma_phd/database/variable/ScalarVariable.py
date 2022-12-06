import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class ScalarVariable(BaseVariable):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id, name=name)
        self._interval: pd.Interval = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = dataframe[self.id].dropna().astype(int)
        self._interval = (
            pd.Interval(left=series.min(), right=series.max(), closed="both")
            if not series.empty
            else None
        )

    @property
    def interval(self) -> pd.Interval:
        return self._interval

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
