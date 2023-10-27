from typing import List, Optional

import catboost
import pandas as pd

from melanoma_phd.database.statistics.TrainingModel import TrainingModel, TrainingModelResult


class CatboostModel(TrainingModel[catboost.CatBoostClassifier]):
    def __init__(
        self,
        kfolds: int,
        random_state: Optional[int] = None,
        categorical_independent_columns: Optional[List[str]] = None,
        **model_params,
    ) -> None:
        super().__init__(kfolds=kfolds, random_state=random_state, **model_params)
        self._categorical_independent_columns: List[str] = categorical_independent_columns or []

    def _fit(
        self,
        independent_df_train: pd.DataFrame,
        target_df_train: pd.DataFrame,
        independent_df_valid: Optional[pd.DataFrame] = None,
        target_df_valid: Optional[pd.DataFrame] = None,
        **fit_params,
    ) -> TrainingModelResult:
        train_pool = self._generate_pool(
            independent_df=independent_df_train, target_df=target_df_train
        )
        if independent_df_valid is not None and target_df_valid is not None:
            valid_pool = self._generate_pool(
                independent_df=independent_df_valid, target_df=target_df_valid
            )
        else:
            valid_pool = None

        model = catboost.CatBoostClassifier(**self._model_params)
        model.fit(
            train_pool, eval_set=valid_pool, metric_period=100, use_best_model=True, **fit_params
        )
        print(model.best_score_["validation"])
        return model

    def calculate_feature_importance(
        self,
        model: catboost.CatBoostClassifier,
        independent_df: pd.DataFrame,
        target_df: pd.DataFrame,
    ) -> pd.DataFrame:
        feature_importance: pd.DataFrame = model.get_feature_importance(
            data=self._generate_pool(independent_df=independent_df, target_df=target_df),
            prettified=True,
        )
        if "Feature Id" in feature_importance.columns:
            feature_importance = feature_importance.set_index("Feature Id")
        return feature_importance

    def predict_proba(
        self, model: catboost.CatBoostClassifier, independent_df: pd.DataFrame
    ) -> pd.DataFrame:
        return model.predict_proba(independent_df)

    def _generate_pool(
        self, independent_df: pd.DataFrame, target_df: pd.DataFrame
    ) -> catboost.Pool:
        pool_params = dict(
            cat_features=self._categorical_independent_columns,
            feature_names=list(independent_df.columns),
        )

        return catboost.Pool(data=independent_df, label=target_df, **pool_params)
