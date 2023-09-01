from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter


class MultiSelectFilter:
    def __init__(self, key_context: str, filter: CategoricalFilter) -> None:
        self._key = f"{key_context}_{filter.name}"
        self._filter = filter
        self._selected_options: List[str] = []

    def select(self) -> None:
        self._selected_options = st.multiselect(
            label=self._filter.name,
            options=self._filter.options(),
            key=self._key,
            default=self.__get_current_options(),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(dataframe, self._selected_options)

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
