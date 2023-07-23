from typing import List, Tuple, Union

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.ScalarFilter import ScalarFilter


class SliderFilter:
    def __init__(self, filter: ScalarFilter) -> None:
        self._filter = filter
        self._selected_interval = None

    def select(self) -> None:
        min_value = self._filter.interval().left.item()
        max_value = self._filter.interval().right.item()
        self._selected_interval = (
            st.slider(
                label=self._filter.name,
                min_value=min_value,
                max_value=max_value,
                value=self.__get_current_value(),
            ),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(dataframe, self._selected_interval)

    def __get_current_value(self) -> Tuple[Union[int, float]]:
        value = tuple([self._filter.interval().left.item(), self._filter.interval().right.item()])
        if self._filter.name in st.session_state:
            value = st.session_state[self._filter.name]
        return value
