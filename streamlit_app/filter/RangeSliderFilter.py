from typing import Any, Dict, List, Optional, Tuple, Union

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
        selected_intervals: List[pd.Interval] = []
        for index in range(self._sliders_number):
            slider_name, slider_key = self.__get_slider_name_key(index)
            selected_interval = st.slider(
                label=slider_name,
                min_value=self._min_value,
                max_value=self._max_value,
                value=self.__get_current_value(
                    index, slider_key, (self._min_value, self._max_value)
                ),
                key=slider_key,
            )
            if selected_interval[0] != self._min_value or selected_interval[1] != self._max_value:
                self._selected_intervals.append(
                    pd.Interval(
                        left=selected_interval[0], right=selected_interval[1], closed="both"
                    )
                )
        self._selected_intervals = selected_intervals

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self._selected_intervals:
            return self._filter.filter(dataframe=dataframe, intervals=self._selected_intervals)
        else:
            return dataframe

    def __get_slider_name_key(self, index: int) -> Tuple[str, str]:
        index_postfix = f" #{index+1}" if self._sliders_number > 1 else ""
        slider_name = f"{self._filter.name}{index_postfix}"
        slider_key = f"{self._key}{index_postfix}"
        return slider_name, slider_key

    def __get_current_value(
        self, index: int, slider_key: str, default: Tuple[Union[int, float], Union[int, float]]
    ) -> Tuple[Union[int, float], Union[int, float]]:
        if self._selected_intervals and index < len(self._selected_intervals):
            return self._selected_intervals[index].left, self._selected_intervals[index].right
        elif slider_key in st.session_state:
            return st.session_state[slider_key]
        else:
            return default

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        for index, interval in enumerate(self._selected_intervals):
            _, slider_key = self.__get_slider_name_key(index)
            dict[slider_key] = (interval.left, interval.right)

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        self._selected_intervals.clear()
        for index in range(self._sliders_number):
            _, slider_key = self.__get_slider_name_key(index)
            if slider_key in dict:
                interval_tuple = dict[slider_key]
                self._selected_intervals.append(
                    pd.Interval(left=interval_tuple[0], right=interval_tuple[1], closed="both")
                )
