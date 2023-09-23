import warnings
from typing import Any, List, Optional, Union

import numpy as np
import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.IteratedScalarVariableStatic import IteratedScalarVariableStatic
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.StatisticFieldName import StatisticFieldName
from melanoma_phd.database.variable.VariableDynamicMixin import (
    BaseDynamicVariableConfig,
    VariableDynamicMixin,
)


class BaseIterationScalarVariableConfig(BaseDynamicVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        iterated_variables: List[IteratedScalarVariableStatic],
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
            required_variables=iterated_variables,
        )
        self.iterated_variables = iterated_variables


class BaseIterationScalarVariable(VariableDynamicMixin, ScalarVariable):
    def __init__(self, config: BaseIterationScalarVariableConfig) -> None:
        super().__init__(config=config)
        self._iterated_variables = config.iterated_variables
        self._interval: Optional[pd.Interval] = None

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        iterated_variables_dataframe = dataframe[iterated_variable_ids]
        self._interval = pd.Interval(
            left=iterated_variables_dataframe.to_numpy(na_value=0).min(),
            right=iterated_variables_dataframe.to_numpy(na_value=0).max(),
            closed="both",
        )

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        return self.get_series(dataframe=dataframe).dropna()

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        values = dataframe[iterated_variable_ids].to_numpy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            series = pd.Series(
                np.nanmean(
                    values,
                    axis=1,
                ),
                index=dataframe.index,
                name=self.id,
            )
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
        series = self.get_series(dataframe=dataframe).dropna()
        count = series.count()
        median = series.median()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        mean = series.mean()
        std_deviation = series.std()
        min = series.min()
        max = series.max()
        return pd.DataFrame(
            data={
                StatisticFieldName.COUNT.value: count,
                StatisticFieldName.MEDIAN.value: median,
                StatisticFieldName.MEAN.value: mean,
                StatisticFieldName.STD_DEVIATION.value: std_deviation,
                StatisticFieldName.MIN_VALUE.value: min,
                StatisticFieldName.MAX_VALUE.value: max,
                StatisticFieldName.QUARTILE_1.value: q1,
                StatisticFieldName.QUARTILE_3.value: q3,
            },
            index=[0],
        )

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        row_name = f"{self.name}   mean ± std (min-max) median"
        value_name = ""
        value = (
            f"{dataframe.iloc[0][StatisticFieldName.MEAN.value]:.2f} ± {dataframe.iloc[0][StatisticFieldName.STD_DEVIATION.value]:.2f}"
            f" ({dataframe.iloc[0][StatisticFieldName.MIN_VALUE.value]:.2f}-{dataframe.iloc[0][StatisticFieldName.MAX_VALUE.value]:.2f})"
            f" {dataframe.iloc[0][StatisticFieldName.MEDIAN.value]:.2f}"
            f" ({dataframe.iloc[0][StatisticFieldName.QUARTILE_1.value]:.2f}-{dataframe.iloc[0][StatisticFieldName.QUARTILE_3.value]:.2f})"
        )
        return [[row_name, value_name, value]]

    def filter(self, dataframe: pd.DataFrame, filter_dataframe: pd.DataFrame) -> pd.DataFrame:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        iterated_filter_dataframe = filter_dataframe.copy()
        iterated_filter_dataframe.columns = iterated_variable_ids
        filtered_dataframe = dataframe.copy()
        for iterated_variable_id in iterated_variable_ids:
            filtered_dataframe.loc[:, iterated_variable_id].where(
                iterated_filter_dataframe[iterated_variable_id], inplace=True
            )
        filtered_dataframe[self.id] = self.get_series(dataframe=filtered_dataframe)
        return filtered_dataframe
