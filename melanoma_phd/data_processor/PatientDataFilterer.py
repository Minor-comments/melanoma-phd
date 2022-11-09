import pandas as pd
from melanoma_phd.data_processor.PatientFilter import PatientFilter


class PatientDataFilterer:
    def __init__(self) -> None:
        pass

    def filter(self, database: pd.DataFrame, filter: PatientFilter) -> pd.DataFrame:
        if filter.population_groups:
            database = database[
                database["GRUPO TTM CORREGIDO"].isin(
                    [group.value for group in filter.population_groups]
                )
            ]
        if filter.current_treatment_types:
            database = database[
                database["TIPO TTM ACTUAL"].isin(
                    [type.value for type in filter.current_treatment_types]
                )
            ]
        return database
