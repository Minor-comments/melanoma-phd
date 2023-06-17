import pandas as pd

from melanoma_phd.database.variable.CategoricalVariable import (
    CategoricalVariable,
    CategoricalVariableConfig,
)
from melanoma_phd.database.variable.VariableStaticMixin import VariableStaticMixin


class CategoricalVariableStatic(VariableStaticMixin, CategoricalVariable):
    def __init__(self, config: CategoricalVariableConfig) -> None:
        super().__init__(config=config)

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        if not self._categories:
            series = super().get_series(dataframe=dataframe)
            unique_values = list(series.dropna().unique())
            self._categories = dict(zip(unique_values, unique_values))

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        series = super().get_series(dataframe=dataframe)
        categories_values = list(self._categories.keys())
        series_unique_values = list(series.dropna().unique())
        if not set(categories_values).issuperset(series_unique_values):
            raise ValueError(
                f"{series_unique_values} categories are not present in {categories_values} variable categories for `{self.id}`"
            )
        if type(categories_values[0]) != type(series_unique_values[0]):
            return series.dropna().astype(type(categories_values[0])).map(self._categories)
        return series.map(self._categories)
