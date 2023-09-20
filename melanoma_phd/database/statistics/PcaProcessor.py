from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
from numpy import log, ndarray
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize

from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


@dataclass
class PcaProcessorCleanedData:
    rows_missing_values_over_threshold: List[int]
    columns_missing_values_over_threshold: List[str]
    other_rows_with_missing_values: List[int]


@dataclass
class PcaProcessorResult:
    pca_df: Optional[pd.DataFrame]
    components: Optional[pd.DataFrame]
    importance: Optional[pd.DataFrame]
    explained_variance_ratio: Optional[ndarray]
    cleaned_data: PcaProcessorCleanedData


class PcaProcessor:
    LOG_COLUMN_SUBSTRINGS = ["Fluo", "Abs"]

    def __init__(
        self,
        pca_feature_variables: List[ScalarVariable],
        n_components: int = 2,
        missing_values_threshold: float = 0.05,
    ) -> None:
        self._pca_feature_variables = pca_feature_variables
        self._n_components = n_components
        self._missing_values_threshold = missing_values_threshold

    def process(
        self,
        df: pd.DataFrame,
    ) -> PcaProcessorResult:
        pca_df = pd.concat(
            [variable.get_series(df) for variable in self._pca_feature_variables],
            axis=1,
        )
        for i, log_column_substring in enumerate(self.LOG_COLUMN_SUBSTRINGS):
            mask = pca_df.columns.str.contains(log_column_substring)
            if i == 0:
                columns_to_log = mask
            else:
                columns_to_log |= mask
        pca_df.loc[:, columns_to_log] = pca_df.loc[:, columns_to_log].apply(
            lambda serie: log(serie, where=(serie.notnull()) & (serie != 0))
        )

        patient_mask = ~pca_df.isnull().all(axis=1)
        rows_missing_values_over_threshold = list(pca_df[~patient_mask].index)
        pca_df = pca_df[patient_mask]

        feature_mask = ~pca_df.isnull().all(axis=0)
        columns_missing_values_over_threshold = list(pca_df.loc[:, ~feature_mask].columns)
        pca_df = pca_df.loc[:, feature_mask]

        patient_mask = pca_df.isnull().sum(axis=1) <= self._missing_values_threshold
        rows_missing_values_over_threshold += list(pca_df[~patient_mask].index)
        pca_df = pca_df[patient_mask]

        feature_mask = pca_df.isnull().sum(axis=0) <= self._missing_values_threshold
        columns_missing_values_over_threshold += list(pca_df.loc[:, ~feature_mask].columns)
        pca_df = pca_df.loc[:, feature_mask]

        all_mask = pca_df.notnull().all(axis=1)
        other_rows_with_missing_values = list(pca_df[~all_mask].index)
        pca_df = pca_df[all_mask]

        cleaned_data = PcaProcessorCleanedData(
            rows_missing_values_over_threshold=sorted(rows_missing_values_over_threshold),
            columns_missing_values_over_threshold=sorted(columns_missing_values_over_threshold),
            other_rows_with_missing_values=other_rows_with_missing_values,
        )

        if len(pca_df.index) == 0:
            return PcaProcessorResult(
                pca_df=None,
                components=None,
                importance=None,
                explained_variance_ratio=None,
                cleaned_data=cleaned_data,
            )
        else:
            pca = PCA(n_components=self._n_components)
            components = pca.fit_transform(normalize(pca_df))

            pca_component_names = [f"PC{i+1}" for i in range(self._n_components)]

            importance = pd.DataFrame(
                pca.components_, columns=pca_df.columns, index=pca_component_names
            )
            importance = importance.T / (importance.max(axis=1) - importance.min(axis=1)).T

            return PcaProcessorResult(
                pca_df=pca_df,
                components=pd.DataFrame(
                    components, columns=pca_component_names, index=pca_df.index
                ),
                importance=importance,
                explained_variance_ratio=pca.explained_variance_ratio_,
                cleaned_data=cleaned_data,
            )
