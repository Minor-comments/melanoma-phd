from copy import deepcopy
from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class CleanedDataInfo:
    rows_missing_values_over_threshold: List[int]
    columns_missing_values_over_threshold: List[str]
    other_rows_with_missing_values: List[int]


@dataclass
class CleanedData:
    data: pd.DataFrame
    info: CleanedDataInfo


class DataCleaner:
    def __init__(self, missing_values_threshold: float = 0.05) -> None:
        self._missing_values_threshold = missing_values_threshold

    def clean_dataframe(self, df: pd.DataFrame) -> CleanedData:
        new_df = deepcopy(df)

        row_mask = ~new_df.isnull().all(axis=1)
        rows_missing_values_over_threshold = list(new_df[~row_mask].index)
        new_df = new_df[row_mask]

        feature_mask = ~new_df.isnull().all(axis=0)
        columns_missing_values_over_threshold = list(new_df.loc[:, ~feature_mask].columns)
        new_df = new_df.loc[:, feature_mask]

        row_mask = new_df.isnull().sum(axis=1) <= self._missing_values_threshold
        rows_missing_values_over_threshold += list(new_df[~row_mask].index)
        new_df = new_df[row_mask]

        feature_mask = new_df.isnull().sum(axis=0) <= self._missing_values_threshold
        columns_missing_values_over_threshold += list(new_df.loc[:, ~feature_mask].columns)
        new_df = new_df.loc[:, feature_mask]

        all_mask = new_df.notnull().all(axis=1)
        other_rows_with_missing_values = list(new_df[~all_mask].index)
        new_df = new_df[all_mask]

        return CleanedData(
            data=new_df,
            info=CleanedDataInfo(
                rows_missing_values_over_threshold=sorted(rows_missing_values_over_threshold),
                columns_missing_values_over_threshold=sorted(columns_missing_values_over_threshold),
                other_rows_with_missing_values=other_rows_with_missing_values,
            ),
        )
