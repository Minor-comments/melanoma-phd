from typing import List

import pandas as pd
import streamlit as st

from melanoma_phd.database.filter.ScalarFilter import ScalarFilter


class SliderFilter:
    def __init__(self, filter: ScalarFilter) -> None:
        self._filter = filter
        self._selected_interval = None

    def select(self) -> None:
        self._selected_interval = st.slider(
            label=self._filter.name,
            value=tuple(
                [self._filter.interval().left.item(), self._filter.interval().right.item()]
            ),
        )

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self._filter.filter(dataframe, self._selected_interval)
