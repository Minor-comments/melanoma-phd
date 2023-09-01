from typing import List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.IterationScalarFilter import IterationScalarFilter


class RangeInputFilter:
    def __init__(
        self,
        key_context: str,
        filter: IterationScalarFilter,
        ranges_number: int = 1,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        step: Optional[Union[int, float]] = 1,
    ) -> None:
        self._key = f"{key_context}_{filter.name}"
        self._filter: IterationScalarFilter = filter
        self._selected_intervals: List[pd.Interval] = []
        self._ranges_number = ranges_number
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        min_iteration = int(self._filter.interval().left)
        max_iteration = int(self._filter.interval().right)
        self._min_value = min_value if min_value and min_value < min_iteration else min_iteration
        self._max_value = max_value if max_value and max_value > max_iteration else max_iteration

    def select(self) -> None:
        self._selected_intervals.clear()
        for index in range(self._ranges_number):
            index_postfix = f" #{index+1}" if self._ranges_number > 1 else ""
            range_name = f"{self._filter.name}{index_postfix}"
            range_key = f"{self._key}{index_postfix}"
            st.write(range_name)
            col0, col1 = st.columns(2)
            with col0:
                range_key_min = f"{range_key}_min"
                selected_min_value = st.number_input(
                    label="Minimum",
                    min_value=self._min_value,
                    max_value=self._max_value,
                    step=self._step,
                    value=self.__get_current_value(range_key_min, self._min_value),
                    key=range_key_min,
                )
            with col1:
                range_key_max = f"{range_key}_max"
                selected_max_value = st.number_input(
                    label="Maximum",
                    min_value=self._min_value,
                    max_value=self._max_value,
                    step=self._step,
                    value=self.__get_current_value(range_key_max, self._max_value),
                    key=range_key_max,
                )
            if selected_min_value != self._min_value or selected_max_value != self._max_value:
                self._selected_intervals.append(
                    pd.Interval(left=selected_min_value, right=selected_max_value, closed="both")
                )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self._selected_intervals:
            return self._filter.filter(dataframe=dataframe, intervals=self._selected_intervals)
        else:
            return dataframe

    def __get_current_value(self, key: str, default: Union[int, float]) -> Union[int, float]:
        if key in st.session_state:
            return st.session_state[key]
        return default
