import math
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd
import prince
from numpy import ndarray
from sklearn.decomposition import PCA, FactorAnalysis, KernelPCA
from sklearn.preprocessing import PowerTransformer

from melanoma_phd.database.statistics.DataCleaner import CleanedDataInfo, DataCleaner
from melanoma_phd.database.statistics.PreProcessor import PreProcessor
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


@dataclass
class PcaProcessorResult:
    pca_df: Optional[pd.DataFrame]
    components: Optional[pd.DataFrame]
    importance: Optional[pd.DataFrame]
    explained_variance_ratio: Optional[ndarray]
    cleaned_data_info: CleanedDataInfo


class PcaProcessor:
    TRANSFORM_COLUMN_SUBSTRINGS = ["Fluo", "Abs", "Tcm/Teff", "Teff/Treg", "EDAD"]

    def __init__(
        self,
        pca_feature_variables: List[ScalarVariable],
        n_components: int = 2,
        missing_values_threshold: float = 0.05,
        use_factor_analysis: bool = False,
    ) -> None:
        self._pca_feature_variables = pca_feature_variables
        self._n_components = n_components
        self._use_factor_analysis = use_factor_analysis
        self._data_cleaner = DataCleaner(missing_values_threshold=missing_values_threshold)
        self._preprocessor = PreProcessor(
            transform_floats=True, substring_transform_columns=self.TRANSFORM_COLUMN_SUBSTRINGS
        )

    def process(
        self,
        df: pd.DataFrame,
    ) -> PcaProcessorResult:
        pca_df = pd.concat(
            [variable.get_series(df) for variable in self._pca_feature_variables],
            axis=1,
        )

        cleaned_data = self._data_cleaner.clean_dataframe(pca_df)
        pca_df = cleaned_data.data

        if len(pca_df.index) == 0:
            return PcaProcessorResult(
                pca_df=None,
                components=None,
                importance=None,
                explained_variance_ratio=None,
                cleaned_data_info=cleaned_data.info,
            )
        else:
            pca_component_names = [f"PC{i+1}" for i in range(self._n_components)]
            transformed_pca_df = self._preprocessor.preprocess(pca_df)

            if self._use_factor_analysis:
                famd = prince.FAMD(
                    n_components=self._n_components,
                    copy=True,
                    check_input=True,
                    engine="scipy",
                    handle_unknown="error",
                )
                components = famd.fit_transform(transformed_pca_df, as_array=True)

                explained_variance_ratio = famd.percentage_of_variance_ / 100

                importance = pd.DataFrame(
                    famd.column_contributions_.values,
                    index=pca_df.columns,
                    columns=pca_component_names,
                )
            else:
                pca = PCA(n_components=self._n_components, svd_solver="full")
                components = pca.fit_transform(transformed_pca_df)

                explained_variance_ratio = pca.explained_variance_ratio_

                importance = pd.DataFrame(
                    pca.components_, columns=pca_df.columns, index=pca_component_names
                ).T

            importance = importance / (importance.max(axis=0) - importance.min(axis=0))
            importance = importance.loc[
                (
                    importance.apply(
                        lambda row: -float(np.linalg.norm(row * explained_variance_ratio)),
                        axis=1,
                    )
                )
                .sort_values()
                .index
            ]

            return PcaProcessorResult(
                pca_df=pca_df,
                components=pd.DataFrame(
                    components, columns=pca_component_names, index=pca_df.index
                ),
                importance=importance,
                explained_variance_ratio=explained_variance_ratio,
                cleaned_data_info=cleaned_data.info,
            )
