from typing import List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.IterationScalarFilter import IterationScalarFilter


class RangeSliderFilter:
    def __init__(
        self,
        key_context: str,
        filter: IterationScalarFilter,
        sliders_number: int = 1,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ) -> None:
        self._key = f"{key_context}_{filter.name}"
        self._filter: IterationScalarFilter = filter
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
            index_postfix = f" #{index+1}" if self._sliders_number > 1 else ""
            slider_name = f"{self._filter.name}{index_postfix}"
            slider_key = f"{self._key}{index_postfix}"
            selected_interval = st.slider(
                label=slider_name,
                min_value=self._min_value,
                max_value=self._max_value,
                value=self.__get_current_value(slider_key),
                key=slider_key,
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

    def __get_current_value(self, slider_key: str) -> Tuple[Union[int, float]]:
        value = tuple([self._min_value, self._max_value])
        if slider_key in st.session_state:
            value = st.session_state[slider_key]
        return value
