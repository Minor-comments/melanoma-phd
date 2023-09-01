import ast
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.ScalarFilter import ScalarFilter


def parse_interval(interval_str: str) -> pd.Interval:
    table = interval_str.maketrans({"[": "(", "]": ")"})
    left_closed = interval_str.startswith("[")
    right_closed = interval_str.endswith("]")
    left, right = ast.literal_eval(interval_str.translate(table))

    closed_type = "neither"
    if left_closed and right_closed:
        closed_type = "both"
    elif left_closed:
        closed_type = "left"
    elif right_closed:
        closed_type = "right"

    return pd.Interval(left, right, closed=closed_type)


class MultiSelectBinFilter:
    def __init__(self, key_context: str, filter: ScalarFilter, bins: Dict[str, str]) -> None:
        self._key = f"{key_context}_{filter.name}"
        self._filter = filter
        interval_bins = {}
        for bin_name, interval_str in bins.items():
            interval_bins[bin_name] = parse_interval(interval_str)
        self._bins = interval_bins
        self._selected_options: List[str] = []

    def select(self) -> None:
        self._selected_options = st.multiselect(
            label=self._filter.name,
            options=self._bins.keys(),
            key=self._key,
            default=self.__get_current_options(),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        intervals = [self._bins[selected_option] for selected_option in self._selected_options]
        return self._filter.filter(dataframe, intervals)

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        dict[self._key] = self._selected_options

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        if self._key in dict:
            self._selected_options = dict[self._key]

    def __get_current_options(self) -> List[str]:
        return (
            self._selected_options
            if self._selected_options
            else st.session_state[self._key]
            if self._key in st.session_state
            else []
        )
