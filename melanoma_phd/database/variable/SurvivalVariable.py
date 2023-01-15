from typing import Any, List, Optional, Tuple, Union
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import pandas as pd
from sksurv.nonparametric import SurvivalFunctionEstimator
from sksurv.util import Surv
from lifelines.statistics import logrank_test, StatisticalResult
from lifelines.plotting import add_at_risk_counts
from lifelines.utils import median_survival_times
import numpy as np

from melanoma_phd.database.variable.BaseDynamicVariable import BaseDynamicVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class SurvivalVariable(ScalarVariable, BaseDynamicVariable):
    def __init__(
        self, id: str, name: str, duration_variable_id: str, events_variable_id: str
    ) -> None:
        super().__init__(id=id, name=name)
        self._duration_variable_id = duration_variable_id
        self._events_variable_id = events_variable_id

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

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
    ) -> pd.DataFrame:
        labels = self.__get_labels(dataframe=dataframe, group_by_id=group_by_id)
        kaplan_meier_fitters = self._calculate_kaplan_meier_fitters(
            dataframe=dataframe, group_by_id=group_by_id
        )
        median_confidence_intervals_ = [
            median_survival_times(kaplan_meier_fitter.confidence_interval_)
            for kaplan_meier_fitter in kaplan_meier_fitters
        ]

        statistics_dataframe = pd.DataFrame(
            {
                "median": [
                    kaplan_meier_fitter.median_survival_time_
                    for kaplan_meier_fitter in kaplan_meier_fitters
                ],
                f"median_lower_{1 - alpha}": [
                    median_confidence_intervals_[i].iloc[0, 0]
                    for i in range(len(kaplan_meier_fitters))
                ],
                f"median_upper_{1 - alpha}": [
                    median_confidence_intervals_[i].iloc[0, 1]
                    for i in range(len(kaplan_meier_fitters))
                ],
            },
            index=[label for label in labels] if len(labels) > 1 else [0],
        )
        if len(labels) > 1:
            statistics_dataframe.index.name = group_by_id

        return statistics_dataframe

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)

    def plot_survival_function(
        self,
        dataframe: pd.DataFrame,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
        figsize: Tuple[int, int] = (10, 6),
        confident_interval: bool = True,
        logx: bool = False,
        at_risk_counts: bool = True,
        show_censors: bool = True,
    ) -> plt.Figure:
        labels = self.__get_labels(dataframe=dataframe, group_by_id=group_by_id)

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)

        statistical_result = self.__get_logrank_test_stats(
            dataframe=dataframe, group_by_id=group_by_id, alpha=alpha
        )
        title = self.__generate_title(statistical_result=statistical_result)
        plt.title(title)

        kaplan_meier_fitters = self._calculate_kaplan_meier_fitters(
            dataframe=dataframe, group_by_id=group_by_id, alpha=alpha
        )

        for i, kaplan_meier_fitter in enumerate(kaplan_meier_fitters):
            shown_label = self.__get_shown_label(
                label=labels[i], labels=labels, group_by_id=group_by_id
            )

            kaplan_meier_fitter.plot_survival_function(
                ax=ax,
                label=shown_label,
                show_censors=show_censors,
                at_risk_counts=False,
                logx=logx,
                ci_show=confident_interval,
            )

        if at_risk_counts:
            add_at_risk_counts(*kaplan_meier_fitters, ax=ax)

        if len(kaplan_meier_fitters) == 1:
            ax.get_legend().remove()

        return fig

    def _calculate_kaplan_meier_fitters(
        self,
        dataframe: pd.DataFrame,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
    ) -> List[KaplanMeierFitter]:
        labels = self.__get_labels(dataframe=dataframe, group_by_id=group_by_id)
        kaplan_meier_fitters: List[KaplanMeierFitter] = []
        for label in labels:
            label_mask = self.__get_label_mask(
                dataframe=dataframe, label=label, group_by_id=group_by_id
            )
            durations = self.__get_durations(dataframe=dataframe[label_mask])
            events = self.__get_events(dataframe=dataframe[label_mask])

            shown_label = self.__get_shown_label(
                label=label, labels=labels, group_by_id=group_by_id
            )

            kaplan_meier_fitter = KaplanMeierFitter()
            kaplan_meier_fitters.append(
                kaplan_meier_fitter.fit(
                    durations=durations,
                    event_observed=events,
                    alpha=alpha,
                    label=shown_label,
                )
            )
        return kaplan_meier_fitters

    def __get_events(self, dataframe: pd.DataFrame) -> np.ndarray:
        return (dataframe[self._events_variable_id].dropna() != 0).to_numpy()

    def __get_durations(self, dataframe: pd.DataFrame) -> np.ndarray:
        return dataframe[self._duration_variable_id].dropna().to_numpy()

    def __get_labels(
        self, dataframe: pd.DataFrame, group_by_id: Optional[str] = None
    ) -> List[Any]:
        if group_by_id is not None:
            labels = list(dataframe[group_by_id].unique())
        else:
            labels = [""]
        return labels

    def __get_label_mask(
        self, dataframe: pd.DataFrame, label: Any, group_by_id: Optional[str] = None
    ) -> Union[pd.Series, List[bool]]:
        labels = self.__get_labels(dataframe=dataframe, group_by_id=group_by_id)
        return (
            dataframe[group_by_id] == label
            if len(labels) > 1 and group_by_id is not None
            else [True] * len(dataframe)
        )

    def __get_shown_label(
        self, label: Any, labels: List[Any], group_by_id: Optional[str] = None
    ) -> str:
        return (
            f"{group_by_id}={label}"
            if len(labels) > 1 and group_by_id is not None
            else ""
        )

    def __get_logrank_test_stats(
        self,
        dataframe: pd.DataFrame,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
    ) -> Optional[StatisticalResult]:
        labels = self.__get_labels(dataframe=dataframe, group_by_id=group_by_id)
        if len(labels) == 2:
            class1 = dataframe[group_by_id] == labels[0]
            class2 = dataframe[group_by_id] == labels[1]

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
