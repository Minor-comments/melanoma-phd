from typing import Optional, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.IterationFilter import IterationFilter


class RangeSliderFilter:
    def __init__(
        self,
        filter: IterationFilter,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> None:
        self._filter: IterationFilter = filter
        self._selected_interval: Optional[pd.Interval] = None
        self._min_value = min_value
        self._max_value = max_value
        min_iteration = int(self._filter.interval().left)
        max_iteration = int(self._filter.interval().right)
        self._min_value = min_value if min_value and min_value < min_iteration else min_iteration
        self._max_value = max_value if max_value and max_value > max_iteration else max_iteration

    def select(self) -> None:
        range = st.slider(
            label=self._filter.name,
            value=tuple([self._min_value, self._max_value]),
        )
        self._selected_interval = pd.Interval(left=range[0], right=range[1], closed="both")

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if (
            self._selected_interval.left == self._min_value
            and self._selected_interval.right == self._max_value
        ):
            return dataframe
        return self._filter.filter(dataframe, self._selected_interval)
