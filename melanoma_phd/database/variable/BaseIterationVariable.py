from copy import deepcopy
from typing import Any, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.BaseDynamicVariable import (
    BaseDynamicVariable,
    BaseDynamicVariableConfig,
)
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.IteratedVariable import IteratedVariable


class BaseIterationVariableConfig(BaseDynamicVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        iterated_variables: List[IteratedVariable],
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
            required_variables=iterated_variables,
        )
        self.iterated_variables = iterated_variables


class BaseIterationVariable(BaseDynamicVariable):
    def __init__(self, config: BaseIterationVariableConfig) -> None:
        super().__init__(config=config)
        self._iterated_variables = config.iterated_variables
        self._interval: Optional[pd.Interval] = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        series = self.get_series(dataframe=dataframe).explode().dropna().astype(int)
        self._interval = (
            pd.Interval(left=series.explode().min(), right=series.explode().max(), closed="both")
            if not series.empty
            else None
        )

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        return super().create_new_series(dataframe=dataframe)

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        series = pd.Series(dataframe[iterated_variable_ids].values.tolist())
        return series

    @property
    def interval(self) -> pd.Interval:
        if self._interval:
            return self._interval
        raise ValueError(f"interval not defined in iteration variable '{self.id}'")

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        if group_by:
            raise NotImplementedError(
                f"Group by for is not implemented on {self.__class__.__name__}"
            )
        series = self.get_series(dataframe=dataframe).explode().dropna()
        count = series.count()
        median = series.median()
        mean = series.mean()
        std_deviation = series.std()
        min = series.min()
        max = series.max()
        return pd.DataFrame(
            data={
                "n": count,
                "median": median,
                "mean": mean,
                "std": std_deviation,
                "min": min,
                "max": max,
            },
            index=[0],
        )

    def filter(self, dataframe: pd.DataFrame, filter_dataframe: pd.DataFrame) -> pd.DataFrame:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        iterated_filter_dataframe = deepcopy(filter_dataframe)
        iterated_filter_dataframe.columns = iterated_variable_ids
        filtered_dataframe = deepcopy(dataframe)
        for iterated_variable_id in iterated_variable_ids:
            filtered_dataframe.loc[:, iterated_variable_id].where(
                iterated_filter_dataframe[iterated_variable_id], inplace=True
            )
        return filtered_dataframe
