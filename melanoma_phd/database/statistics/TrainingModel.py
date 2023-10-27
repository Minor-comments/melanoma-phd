from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Generic, List, Optional, Tuple, TypeVar

import numpy as np
import pandas as pd
from catboost.utils import select_threshold
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import KFold

InternalModel = TypeVar("InternalModel")


@dataclass
class TrainingModelResult(Generic[InternalModel]):
    model: InternalModel
    metrics: pd.DataFrame
    probabilities: pd.DataFrame
    feature_importance: pd.DataFrame
    fpr_mean: np.ndarray
    tpr_mean: np.ndarray
    tpr_upper: Optional[np.ndarray] = None
    tpr_lower: Optional[np.ndarray] = None


class TrainingModel(Generic[InternalModel]):
    def __init__(self, kfolds: int, random_state: Optional[int] = None, **model_params) -> None:
        self._kfolds = kfolds
        self._random_state = random_state
        self._model_params = model_params

    @abstractmethod
    def _fit(
        self,
        independent_df_train: pd.DataFrame,
        target_df_train: pd.DataFrame,
        independent_df_valid: Optional[pd.DataFrame] = None,
        target_df_valid: Optional[pd.DataFrame] = None,
        **fit_params,
    ) -> InternalModel:
        pass

    @abstractmethod
    def calculate_feature_importance(
        self, model: InternalModel, independent_df: pd.DataFrame, target_df: pd.DataFrame
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def predict_proba(self, model: InternalModel, independent_df: pd.DataFrame) -> pd.DataFrame:
        pass

    def predict(self, probabilities: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        return probabilities.applymap(lambda x: 1 if x > threshold else 0)

    def fit(
        self, independent_df: pd.DataFrame, target_df: pd.DataFrame, **fit_params
    ) -> TrainingModelResult[InternalModel]:
        feature_importance = None
        probabilities = None
        metrics = defaultdict(list)
        intermediate_results = defaultdict(list)
        for fold, (train_idx, valid_idx) in enumerate(
            KFold(n_splits=self._kfolds, random_state=self._random_state, shuffle=True).split(
                target_df
            )
        ):
            independent_df_train = independent_df.iloc[train_idx]
            independent_df_valid = independent_df.iloc[valid_idx]
            target_df_train = target_df.iloc[train_idx]
            target_df_valid = target_df.iloc[valid_idx]

            model = self._fit(
                independent_df_train,
                target_df_train,
                independent_df_valid,
                target_df_valid,
                **fit_params,
            )

            fold_feature_importance = self.calculate_feature_importance(
                model=model, independent_df=independent_df_valid, target_df=target_df_valid
            )
            if feature_importance is not None:
                feature_importance += fold_feature_importance / self._kfolds
            else:
                feature_importance = fold_feature_importance / self._kfolds

            fold_probabilities = pd.DataFrame(
                self.predict_proba(model=model, independent_df=independent_df_valid),
                index=target_df_valid.index,
            )
            if probabilities is not None:
                probabilities = pd.concat(
                    [
                        probabilities,
                        fold_probabilities,
                    ],
                    axis=0,
                )
            else:
                probabilities = fold_probabilities

            probabilities = fold_probabilities.loc[target_df_valid.index]

            if len(fold_probabilities.columns) == 2:
                y_score = fold_probabilities.iloc[:, [-1]]
            else:
                y_score = fold_probabilities
            predictions = self.predict(y_score)
            fpr, tpr, _ = roc_curve(y_true=target_df_valid, y_score=y_score)
            intermediate_results["fpr"].append(fpr)
            intermediate_results["tpr"].append(tpr)
            metrics["AUC"].append(roc_auc_score(y_true=target_df_valid, y_score=y_score))
            metrics["Accuracy"].append(accuracy_score(y_true=target_df_valid, y_pred=predictions))
            metrics["BalancedAccuracy"].append(
                balanced_accuracy_score(y_true=target_df_valid, y_pred=predictions)
            )
            metrics["Recall"].append(recall_score(y_true=target_df_valid, y_pred=predictions))
            metrics["Precision"].append(precision_score(y_true=target_df_valid, y_pred=predictions))
            metrics["F1"].append(f1_score(y_true=target_df_valid, y_pred=predictions))

        assert probabilities is not None and len(
            probabilities.index
        ), "Probabilities should not be empty"
        assert feature_importance is not None and len(
            feature_importance.index
        ), "Feature importance should not be empty"

        feature_importance = feature_importance.sort_values(
            ascending=False, by=list(feature_importance.columns.astype(str))[-1]
        )

        metrics_df = pd.DataFrame(metrics)
        metrics_df.index.name = "Fold"
        metrics_df.loc["Mean", :] = metrics_df.mean()

        fpr_mean = np.linspace(0, 1, 100)
        interp_tprs = []
        for i in range(self._kfolds):
            fpr = intermediate_results["fpr"][i]
            tpr = intermediate_results["tpr"][i]
            interp_tpr = np.interp(fpr_mean, fpr, tpr)
            interp_tpr[0] = 0.0
            interp_tprs.append(interp_tpr)
        tpr_mean = np.mean(interp_tprs, axis=0)
        tpr_mean[-1] = 1.0
        tpr_std = 2 * np.std(interp_tprs, axis=0)
        tpr_upper = np.clip(tpr_mean + tpr_std, 0, 1)
        tpr_lower = tpr_mean - tpr_std

        return TrainingModelResult(
            model=model,
            metrics=metrics_df,
            probabilities=probabilities,
            feature_importance=feature_importance,
            fpr_mean=fpr_mean,
            tpr_mean=tpr_mean,
            tpr_upper=tpr_upper,
            tpr_lower=tpr_lower,
        )
