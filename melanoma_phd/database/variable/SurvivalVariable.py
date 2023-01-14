from typing import Any, List, Optional, Tuple, Union
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import pandas as pd
from sksurv.nonparametric import SurvivalFunctionEstimator
from sksurv.util import Surv
from lifelines.statistics import logrank_test, StatisticalResult
from lifelines.plotting import add_at_risk_counts
import numpy as np

from melanoma_phd.database.variable.BaseDynamicVariable import BaseDynamicVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class SurvivalVariable(ScalarVariable, BaseDynamicVariable):
    def __init__(
        self,
        id: str,
        name: str,
        duration_variable_id: str,
        events_variable_id: str,
        group_by_id: Optional[str] = None,
    ) -> None:
        super().__init__(id=id, name=name)
        self._duration_variable_id = duration_variable_id
        self._events_variable_id = events_variable_id
        self._group_by_id = group_by_id

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    def create_new_series(self, dataframe: pd.DataFrame) -> pd.Series:
        estimator = SurvivalFunctionEstimator()
        events = self.__get_events(dataframe=dataframe)
        durations = self.__get_durations(dataframe=dataframe)
        estimator.fit(Surv.from_arrays(events, durations))
        return dataframe[self._duration_variable_id].map(
            lambda value: estimator.predict_proba([value])[0], na_action="ignore"
        )

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return super().descriptive_statistics(dataframe=dataframe)

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)

    def plot_survival_function(
        self,
        dataframe: pd.DataFrame,
        alpha: float = 0.05,
        figsize: Tuple[int, int] = (10, 6),
        confident_interval: bool = True,
        logx: bool = False,
        at_risk_counts: bool = True,
        show_censors: bool = True,
    ) -> plt.Figure:
        labels = self.__get_labels(dataframe=dataframe)

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)

        statistical_result = self.__get_logrank_test_stats(
            dataframe=dataframe, labels=labels, alpha=alpha
        )
        title = self.__generate_title(statistical_result=statistical_result)
        plt.title(title)

        kmfs = []
        for label in labels:
            label_mask = self.__get_label_mask(
                dataframe=dataframe, label=label, labels=labels
            )
            durations = self.__get_durations(dataframe=dataframe[label_mask])
            events = self.__get_events(dataframe=dataframe[label_mask])

            shown_label = self.__get_shown_label(label=label, labels=labels)

            kmf = KaplanMeierFitter()
            kmfs.append(
                kmf.fit(durations=durations, event_observed=events, label=shown_label)
            )

            kmf.plot_survival_function(
                ax=ax,
                label=shown_label,
                show_censors=show_censors,
                at_risk_counts=False,
                logx=logx,
                ci_show=confident_interval,
            )

        if at_risk_counts:
            add_at_risk_counts(*kmfs, ax=ax)

        if len(labels) == 1:
            ax.get_legend().remove()

        return fig

    def __get_events(self, dataframe: pd.DataFrame) -> np.ndarray:
        return (dataframe[self._events_variable_id].dropna() != 0).to_numpy()

    def __get_durations(self, dataframe: pd.DataFrame) -> np.ndarray:
        return dataframe[self._duration_variable_id].dropna().to_numpy()

    def __get_labels(self, dataframe: pd.DataFrame) -> List[Any]:
        if self._group_by_id is not None:
            labels = list(dataframe[self._group_by_id].unique())
        else:
            labels = [""]
        return labels

    def __get_label_mask(
        self, dataframe: pd.DataFrame, label: Any, labels: List[Any]
    ) -> Union[pd.Series, List[bool]]:
        return (
            dataframe[self._group_by_id] == label
            if len(labels) > 1
            else [True] * len(dataframe)
        )

    def __get_shown_label(self, label: Any, labels: List[Any]) -> str:
        return f"{self._group_by_id}={label}" if len(labels) > 1 else ""

    def __get_logrank_test_stats(
        self, dataframe: pd.DataFrame, labels: List[Any] = [], alpha: float = 0.05
    ) -> Optional[StatisticalResult]:
        if len(labels) == 2:
            class1 = dataframe[self._group_by_id] == labels[0]
            class2 = dataframe[self._group_by_id] == labels[1]

            durations = self.__get_durations(dataframe=dataframe)
            events = self.__get_events(dataframe=dataframe)

            output_logrank = logrank_test(
                durations[class1],
                durations[class2],
                events[class1],
                events[class2],
                alpha=(1 - alpha),
            )
            return output_logrank
        return None

    def __generate_title(self, statistical_result: Optional[StatisticalResult]) -> str:
        title = "Survival function"
        if statistical_result is not None:
            title += "\nLogrank P-Value = %.5f" % (statistical_result.p_value)
        return title
