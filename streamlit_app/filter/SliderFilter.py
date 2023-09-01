from typing import Any, Dict, Tuple, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.ScalarFilter import ScalarFilter


class SliderFilter:
    def __init__(self, key_context: str, filter: ScalarFilter) -> None:
        self._key = f"{key_context}_{filter.name}"
        self._filter = filter
        self._selected_interval: Tuple[Union[int, float], Union[int, float]] = None

    def select(self) -> None:
        min_value = self._filter.interval().left.item()
        max_value = self._filter.interval().right.item()
        self._selected_interval = st.slider(
            label=self._filter.name,
            min_value=min_value,
            max_value=max_value,
            value=self.__get_current_value(),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(
            dataframe,
            pd.Interval(
                left=self._selected_interval[0],
                right=self._selected_interval[1],
                closed="both",
            ),
        )

    def __get_current_value(self) -> Tuple[Union[int, float], Union[int, float]]:
        if self._selected_interval:
            return self._selected_interval[0], self._selected_interval[1]
        elif self._key in st.session_state:
            return st.session_state[self._key]
        else:
            return self._filter.interval().left.item(), self._filter.interval().right.item()

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        dict[self._key] = self._selected_interval

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        if self._key in dict:
            self._selected_interval = dict[self._key]
