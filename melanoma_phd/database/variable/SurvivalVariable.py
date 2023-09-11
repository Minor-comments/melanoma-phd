from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import StatisticalResult, logrank_test
from lifelines.utils import median_survival_times

from melanoma_phd.database.variable.BaseVariable import BaseVariable, VariableStatisticalType
from melanoma_phd.database.variable.VariableDynamicMixin import (
    BaseDynamicVariableConfig,
    VariableDynamicMixin,
)


class SurvivalVariableConfig(BaseDynamicVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        duration_variable_id: str,
        events_variable_id: str,
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
            required_ids=[duration_variable_id, events_variable_id],
        )
        self.duration_variable_id = duration_variable_id
        self.events_variable_id = events_variable_id


@dataclass
class EventsDurations:
    events: np.ndarray
    durations: np.ndarray


class SurvivalVariable(VariableDynamicMixin, BaseVariable):
    def __init__(self, config: SurvivalVariableConfig) -> None:
        super().__init__(config=config)
        self._duration_variable_id = config.duration_variable_id
        self._events_variable_id = config.events_variable_id

    @staticmethod
    def statistical_type() -> VariableStatisticalType:
        return VariableStatisticalType.SCALAR

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        return super().create_new_series(dataframe=dataframe)

    def descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        percentile: float = 0.75,
        alpha: float = 0.05,
        **kwargs: Any,
    ) -> pd.DataFrame:
        if isinstance(group_by, list):
            if len(group_by) > 1:
                raise NotImplementedError(
                    f"Group by list of variables is not implemented on {self.__class__.__name__}"
                )
            else:
                group_by = group_by[0]

        group_by_data = group_by.get_series(dataframe=dataframe) if group_by else None
        group_by_id = group_by.id if group_by else None

        labels = self.get_labels(group_by_data=group_by_data)
        kaplan_meier_fitters = self.calculate_kaplan_meier_fitters(
            dataframe=dataframe, group_by_data=group_by_data, group_by_id=group_by_id, alpha=alpha
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
                f"percentile {percentile}": [
                    kaplan_meier_fitter.percentile(percentile)
                    for kaplan_meier_fitter in kaplan_meier_fitters
                ],
            },
            index=[label for label in labels] if len(labels) > 1 else [0],
        )
        if len(labels) > 1:
            statistics_dataframe.index.name = group_by_id

        return statistics_dataframe

    def format_descriptive_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> List[List[str]]:
        column_median = dataframe["median"]
        column_median_lower = dataframe[
            dataframe.columns[dataframe.columns.str.startswith(f"median_lower")]
        ].iloc[:, 0]
        column_median_upper = dataframe[
            dataframe.columns[dataframe.columns.str.startswith(f"median_upper")]
        ].iloc[:, 0]
        column_percentile = dataframe[
            dataframe.columns[dataframe.columns.str.startswith(f"percentile")]
        ].iloc[:, 0]
        row_name = f"{self.name} {column_median.name} ({column_median_lower.name}, {column_median_upper.name}) {column_percentile.name}"
        value_name = ""
        value = f"{column_median.values} {column_median_lower.values},{column_median_upper.values}) {column_percentile.values}"
        return [[row_name, value_name, value]]

    def calculate_kaplan_meier_fitters(
        self,
        dataframe: pd.DataFrame,
        group_by_data: Optional[pd.Series] = None,
        group_by_id: Optional[str] = None,
        alpha: float = 0.05,
    ) -> List[KaplanMeierFitter]:
        labels = self.get_labels(group_by_data=group_by_data)
        kaplan_meier_fitters: List[KaplanMeierFitter] = []
        for label in labels:
            label_mask = self.get_label_mask(
                dataframe=dataframe, label=label, group_by_data=group_by_data
            )
            events_durations = self.get_events_durations(dataframe=dataframe[label_mask])
            durations = events_durations.durations
            events = events_durations.events

            shown_label = self.get_shown_label(label=label, labels=labels, group_by_id=group_by_id)

            if len(durations) and len(events):
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

    def get_events_durations(self, dataframe: pd.DataFrame) -> EventsDurations:
        events, durations = self.__filter_events_durations_common_index(dataframe=dataframe)

        return EventsDurations(
            events=events.to_numpy(),
            durations=durations.to_numpy(),
        )

    def get_labels(self, group_by_data: Optional[pd.Series] = None) -> List[Any]:
        if group_by_data is not None:
            labels = list(group_by_data.dropna().unique())
        else:
            labels = [""]
        return labels

    def get_label_mask(
        self, dataframe: pd.DataFrame, label: Any, group_by_data: Optional[pd.Series] = None
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
        return f"{group_by_id}={label}" if len(labels) > 1 and group_by_id is not None else ""

    def get_logrank_test_stats(
        self,
        dataframe: pd.DataFrame,
        group_by_data: Optional[pd.Series] = None,
        alpha: float = 0.05,
    ) -> Optional[StatisticalResult]:
        labels = self.get_labels(group_by_data=group_by_data)
        if len(labels) == 2 and group_by_data is not None:
            events_series, durations_series = self.__filter_events_durations_common_index(
                dataframe=dataframe
            )
            group_by_data, _ = self.__filter_common_index(group_by_data, events_series)
            class1 = group_by_data == labels[0]
            class2 = group_by_data == labels[1]

            durations = durations_series.to_numpy()
            events = events_series.to_numpy()

            output_logrank = logrank_test(
                durations[class1],
                durations[class2],
                events[class1],
                events[class2],
                alpha=(1 - alpha),
            )
            return output_logrank
        return None

    def __filter_events_durations_common_index(
        self, dataframe: pd.DataFrame
    ) -> Tuple[pd.Series, pd.Series]:
        events = dataframe[self._events_variable_id].dropna() != 0
        durations = dataframe[self._duration_variable_id].dropna()
        return self.__filter_common_index(events, durations)

    def __filter_common_index(
        self, series0: pd.Series, series1: pd.Series
    ) -> Tuple[pd.Series, pd.Series]:
        return (
            series0[series0.index.isin(series1.index)],
            series1[series1.index.isin(series0.index)],
        )
