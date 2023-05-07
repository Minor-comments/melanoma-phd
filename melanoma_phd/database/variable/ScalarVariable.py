from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.variable.BaseVariable import BaseVariable, PValue
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable


class ScalarVariable(BaseVariable):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id, name=name)
        self._interval: Optional[pd.Interval] = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = self.get_series(dataframe=dataframe).dropna().astype(int)
        self._interval = (
            pd.Interval(left=series.min(), right=series.max(), closed="both")
            if not series.empty
            else None
        )

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        return super().get_series(dataframe=dataframe)

    @property
    def interval(self) -> pd.Interval:
        if self._interval:
            return self._interval
        raise ValueError(f"interval not defined in scalar variable '{self.id}'")

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        if group_by is None:
            series = self.get_series(dataframe=dataframe).dropna()
            median = series.median()
            mean = series.mean()
            std_deviation = series.std()
            min = series.min()
            max = series.max()
            return pd.DataFrame(
                data={
                    "median": median,
                    "mean": mean,
                    "std": std_deviation,
                    "min": min,
                    "max": max,
                },
                index=[0],
            )
        else:
            group_by_list = [group_by] if isinstance(group_by, BaseVariable) else group_by
            group_by_data = [
                group_by_variable.get_series(dataframe=dataframe)
                for group_by_variable in group_by_list
            ]
            return dataframe.groupby(group_by_data)[self.id].agg(
                ["median", "mean", "std", "min", "max"], dropna=True
            )

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)

    def _get_data_by_categories(
        self, dataframe: pd.DataFrame, category_variable: CategoricalVariable
    ) -> Tuple[pd.Series, ...]:
        return tuple(
            self._get_non_na_data(data=data)
            for _, data in dataframe.groupby(category_variable._get_non_na_data(data=dataframe))
        )
