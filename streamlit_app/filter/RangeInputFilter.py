from typing import Any, Dict, List, Optional, Tuple, Union

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
        selected_intervals: List[pd.Interval] = []
        for index in range(self._ranges_number):
            range_name, range_key_min, range_key_max = self.__get_number_input_name_key(index)
            st.write(range_name)
            col0, col1 = st.columns(2)
            with col0:
                selected_min_value = st.number_input(
                    label="Minimum",
                    min_value=self._min_value,
                    max_value=self._max_value,
                    step=self._step,
                    key=range_key_min,
                    value=self.__get_current_min_value(index, range_key_min, self._min_value),
                )
            with col1:
                selected_max_value = st.number_input(
                    label="Maximum",
                    min_value=self._min_value,
                    max_value=self._max_value,
                    step=self._step,
                    key=range_key_max,
                    value=self.__get_current_max_value(index, range_key_max, self._max_value),
                )
            if selected_min_value != self._min_value or selected_max_value != self._max_value:
                selected_intervals.append(
                    pd.Interval(left=selected_min_value, right=selected_max_value, closed="both")
                )

        self._selected_intervals = selected_intervals

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self._selected_intervals:
            return self._filter.filter(dataframe=dataframe, intervals=self._selected_intervals)
        else:
            return dataframe

    def __get_current_min_value(
        self, index: int, key: str, default: Union[int, float]
    ) -> Union[int, float]:
        if self._selected_intervals and index < len(self._selected_intervals):
            return self._selected_intervals[index].left
        elif key in st.session_state:
            return st.session_state[key]
        else:
            return default

    def __get_current_max_value(
        self, index: int, key: str, default: Union[int, float]
    ) -> Union[int, float]:
        if self._selected_intervals and index < len(self._selected_intervals):
            return self._selected_intervals[index].right
        elif key in st.session_state:
            return st.session_state[key]
        else:
            return default

    def __get_number_input_name_key(self, index: int) -> Tuple[str, str, str]:
        index_postfix = f" #{index+1}" if self._ranges_number > 1 else ""
        range_name = f"{self._filter.name}{index_postfix}"
        range_key = f"{self._key}{index_postfix}"
        range_key_min = f"{range_key}_min"
        range_key_max = f"{range_key}_max"
        return range_name, range_key_min, range_key_max

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        for index, interval in enumerate(self._selected_intervals):
            _, range_key_min, range_key_max = self.__get_number_input_name_key(index)
            dict[range_key_min] = interval.left
            dict[range_key_max] = interval.right

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        self._selected_intervals.clear()
        for index in range(self._ranges_number):
            _, range_key_min, range_key_max = self.__get_number_input_name_key(index)
            if range_key_min in dict and range_key_max in dict:
                self._selected_intervals.append(
                    pd.Interval(left=dict[range_key_min], right=dict[range_key_max], closed="both")
                )
