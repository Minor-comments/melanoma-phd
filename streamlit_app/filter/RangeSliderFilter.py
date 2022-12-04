from typing import List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.ScalarFilter import ScalarFilter


class RangeSliderFilter:
    def __init__(self, filter: ScalarFilter) -> None:
        self._filter = filter
        self._selected_range = None

    def select(self) -> None:
        self._selected_range = st.slider(
            label=self._filter.name,
            value=self._filter.range(),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(dataframe, self._selected_range)
