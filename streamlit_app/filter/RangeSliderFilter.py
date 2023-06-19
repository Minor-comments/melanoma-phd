from typing import List, Optional, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.IterationFilter import IterationFilter


class RangeSliderFilter:
    def __init__(
        self,
        filter: IterationFilter,
        sliders_number: int = 1,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> None:
        self._filter: IterationFilter = filter
        self._selected_intervals: List[pd.Interval] = []
        self._sliders_number = sliders_number
        self._min_value = min_value
        self._max_value = max_value
        min_iteration = int(self._filter.interval().left)
        max_iteration = int(self._filter.interval().right)
        self._min_value = min_value if min_value and min_value < min_iteration else min_iteration
        self._max_value = max_value if max_value and max_value > max_iteration else max_iteration

    def select(self) -> None:
        self._selected_intervals.clear()
        for index in range(self._sliders_number):
            index_postfix = f" {index+1}" if self._sliders_number > 1 else ""
            selected_interval = st.slider(
                label=f"{self._filter.name}{index_postfix}",
                value=tuple([self._min_value, self._max_value]),
            )
            if selected_interval[0] != self._min_value or selected_interval[1] != self._max_value:
                self._selected_intervals.append(
                    pd.Interval(
                        left=selected_interval[0], right=selected_interval[1], closed="both"
                    )
                )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self._selected_intervals:
            return self._filter.filter(dataframe=dataframe, intervals=self._selected_intervals)
        else:
            return dataframe
