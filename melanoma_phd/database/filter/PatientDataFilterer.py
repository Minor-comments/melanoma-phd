from typing import List

import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.PatientDatabase import PatientDatabase


class PatientDataFilterer:
    def __init__(self) -> None:
        pass

    def filter(self, database: PatientDatabase, filters: List[BaseFilter]) -> pd.DataFrame:
        filtered_dataframe = database.dataframe
        for filter in filters:
            filtered_dataframe = filter.filter(filtered_dataframe)
        return filtered_dataframe
