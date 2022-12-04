from typing import List

import pandas as pd

from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.PatientDatabase import PatientDatabase


class PatientDataFilterer:
    def __init__(self) -> None:
        pass

    def filter(self, database: PatientDatabase, filters: List[BaseFilter]) -> pd.DataFrame:
        for filter in filters:
            filtered_dataframe = filter.filter(database.dataframe)
        return filtered_dataframe
