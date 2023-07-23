from typing import List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter


class MultiSelectFilter:
    def __init__(self, filter: CategoricalFilter) -> None:
        self._filter = filter
        self._selected_options = []

    def select(self) -> None:
        options = self.__get_current_options()
        self._selected_options = st.multiselect(
            label=self._filter.name,
            options=self._filter.options(),
            key=self._filter.name,
            default=options,
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(dataframe, self._selected_options)

    def __get_current_options(self) -> List[str]:
        options = []
        if self._filter.name in st.session_state:
            options = st.session_state[self._filter.name]
        return options
