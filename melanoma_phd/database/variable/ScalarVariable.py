import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class ScalarVariable(BaseVariable):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id, name=name)

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        series = dataframe[self.id]
        median = series.median()
        mean = series.mean()
        std_deviation = series.std()
        min = series.min()
        max = series.max()
        return pd.DataFrame(
            data={"median": median, "mean": mean, "std": std_deviation, "min": min, "max": max},
            index=[0],
        )
