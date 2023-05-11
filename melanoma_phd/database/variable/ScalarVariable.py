from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.StatisticFieldName import StatisticFieldName


@dataclass
class ScalarVariableConfig(BaseVariableConfig):
    pass


class ScalarVariable(BaseVariable):
    def __init__(self, config: ScalarVariableConfig) -> None:
        super().__init__(config=config)
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
        if not group_by:
            series = self.get_series(dataframe=dataframe).dropna()
            count = series.count()
            median = series.median()
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
                },
                index=[0],
            )
        else:
            group_by_list = [group_by] if isinstance(group_by, BaseVariable) else group_by
            group_by_data = [
                group_by_variable.get_series(dataframe=dataframe)
                for group_by_variable in group_by_list
            ]
            result = dataframe.groupby(group_by_data)[self.id].agg(
                [
                    StatisticFieldName.MEDIAN.value,
                    StatisticFieldName.MEAN.value,
                    StatisticFieldName.STD_DEVIATION.value,
                    StatisticFieldName.MIN_VALUE.value,
                    StatisticFieldName.MAX_VALUE.value,
                ],
            )
            return result

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)

    def _get_data_by_categories(
        self, dataframe: pd.DataFrame, category_variable: CategoricalVariable
    ) -> Tuple[pd.Series, ...]:
        return tuple(
            self._get_non_na_data(data=data)
            for _, data in dataframe.groupby(category_variable._get_non_na_data(data=dataframe))
        )
