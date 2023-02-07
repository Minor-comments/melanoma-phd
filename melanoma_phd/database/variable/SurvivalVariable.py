from typing import Any, List, Optional, Tuple, Union
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
import pandas as pd
from lifelines.statistics import logrank_test, StatisticalResult
from lifelines.plotting import add_at_risk_counts
from lifelines.utils import median_survival_times
import numpy as np
from melanoma.melanoma_phd.database.variable.BaseVariable import BaseVariable

from melanoma_phd.database.variable.BaseDynamicVariable import BaseDynamicVariable


class SurvivalVariable(BaseDynamicVariable):
    def __init__(
        self, id: str, name: str, duration_variable_id: str, events_variable_id: str
    ) -> None:
        super().__init__(
            id=id, name=name, required_ids=[duration_variable_id, events_variable_id]
        )
        self._duration_variable_id = duration_variable_id
        self._events_variable_id = events_variable_id

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        return super().create_new_series(dataframe=dataframe)

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        alpha: float = 0.05,
    ) -> pd.DataFrame:
        if isinstance(group_by, list):
            raise NotImplementedError(
                f"Group by list of variables is not implemented on {self.__class__.__name__}"
            )

        group_by_data = group_by.get_series(dataframe=dataframe) if group_by else None
        group_by_id = group_by.id

        labels = self.get_labels(dataframe=dataframe, group_by_data=group_by_data)
        kaplan_meier_fitters = self.calculate_kaplan_meier_fitters(
            dataframe=dataframe, group_by_data=group_by_data, group_by_id=group_by_id
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

    def calculate_kaplan_meier_fitters(
        self,
        dataframe: pd.DataFrame,
        group_by_data: Optional[pd.Series] = None,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
    ) -> List[KaplanMeierFitter]:
        labels = self.get_labels(dataframe=dataframe, group_by_data=group_by_data)
        kaplan_meier_fitters: List[KaplanMeierFitter] = []
        for label in labels:
            label_mask = self.get_label_mask(
                dataframe=dataframe, label=label, group_by_data=group_by_data
            )
            durations = self.get_durations(dataframe=dataframe[label_mask])
            events = self.get_events(dataframe=dataframe[label_mask])

            shown_label = self.get_shown_label(
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

    def get_events(self, dataframe: pd.DataFrame) -> np.ndarray:
        return (dataframe[self._events_variable_id].dropna() != 0).to_numpy()

    def get_durations(self, dataframe: pd.DataFrame) -> np.ndarray:
        return dataframe[self._duration_variable_id].dropna().to_numpy()

    def get_labels(
        self, group_by_data: Optional[pd.Series] = None
    ) -> List[Any]:
        if group_by_data is not None:
            labels = list(group_by_data.unique())
        else:
            labels = [""]
        return labels

    def get_label_mask(
        self, dataframe: pd.DataFrame, label: Any, group_by_data: Optional[str] = None
    ) -> Union[pd.Series, List[bool]]:
        labels = self.get_labels(group_by_data=group_by_data)
        return (
            group_by_data == label
            if len(labels) > 1 and group_by_data is not None
            else [True] * len(dataframe)
        )

    def get_shown_label(
        self, label: Any, labels: List[Any], group_by_id: Optional[str] = None
    ) -> str:
        return (
            f"{group_by_id}={label}"
            if len(labels) > 1 and group_by_id is not None
            else ""
        )

    def get_logrank_test_stats(
        self,
        dataframe: pd.DataFrame,
        group_by_data: Optional[str] = None,
        alpha: float = 0.05,
    ) -> Optional[StatisticalResult]:
        labels = self.get_labels(group_by_data=group_by_data)
        if len(labels) == 2:
            class1 = group_by_data == labels[0]
            class2 = group_by_data == labels[1]

            durations = self.get_durations(dataframe=dataframe)
            events = self.get_events(dataframe=dataframe)

            output_logrank = logrank_test(
                durations[class1],
                durations[class2],
                events[class1],
                events[class2],
                alpha=(1 - alpha),
            )
            return output_logrank
        return None
