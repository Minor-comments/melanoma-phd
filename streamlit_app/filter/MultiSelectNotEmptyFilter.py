from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.NotEmptyVariableFilter import NotEmptyVariableFilter


class MultiSelectNotEmptyFilter:
    EMPTY_OPTON: str = "Choose an option"

    def __init__(
        self, label: str, key_context: str, filters: List[NotEmptyVariableFilter]
    ) -> None:
        self.label: str = label
        self._key: str = f"{key_context}_" + "_".join(filter.name for filter in filters)
        self._filters: Dict[str, NotEmptyVariableFilter] = {
            filter.name: filter for filter in filters
        }
        self._selected_option: str

    def select(self) -> None:
        options = list(self._filters.keys())
        options.insert(0, self.EMPTY_OPTON)
        self._selected_option = st.selectbox(
            label=self.label,
            options=options,
            key=self._key,
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return (
            self._filters[self._selected_option].filter(dataframe)
            if self._selected_option != self.EMPTY_OPTON
            else dataframe
        )

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        dict[self._key] = self._selected_option

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        if self._key in dict:
            self._selected_option = dict[self._key]
