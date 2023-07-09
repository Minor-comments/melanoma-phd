from typing import List

import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter


class PatientDataFilterer:
    def __init__(self) -> None:
        pass

    def filter(self, dataframe: pd.DataFrame, filters: List[BaseFilter]) -> pd.DataFrame:
        for filter in filters:
            dataframe = filter.filter(dataframe)
        return dataframe
