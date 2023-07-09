from collections import defaultdict
from typing import Any, Dict, List

import pandas as pd


class Patient:
    def __init__(self, patient_id: int, series: pd.Series) -> None:
        self._id: int = patient_id
        self._dataframe: pd.Series = series

    @property
    def id(self) -> int:
        return self._id

    def create_time_series(
        self,
        time_variable_name: str,
        value_variable_name: str,
        range: List[int],
    ) -> pd.DataFrame:
        """Return a time series dataframe getting as variable time the provided `time_variable_name` and value variable from `value_variable_name`.
        The `range` parameter indicates the index of each repetition, that must be present in variable name.
        The variable names must contain the character placeholder `{N}` in order to indicate where the index is present in the name.
        The result is a dataframe with columns labaled as provided `time_variable_name` and `value_variable_name` without the `{N}` notation.
        Example: `Extraction Date {N}` as time variable name and `Positive {N} Result` as value variable name, where real variables are `Extraction Date 1`, `Extraction Date 2`
        and `Positive 1 Result`, `Positive 2 Result`, as well as `range` parameter must be [1, 2]. The result will have `Extraction Date` and `Positive Result` variables.

        Args:
            time_variable_name (str): variable name of the time series.
            value_variable_name (str): variable name of the time series.
            range (List[int]): list of the index of each repetition.
        Returns:
            pd.DataFrame: Time series dataframe.
        """
        if not "{N}" in time_variable_name:
            raise ValueError(
                f"Time variable name '"
                + time_variable_name
                + "' has to incorporate {N} characters for indicating index position"
            )
        if not "{N}" in value_variable_name:
            raise ValueError(
                f"Value variable name '"
                + value_variable_name
                + "' has to incorporate {N} characters for indicating index position"
            )
        new_time_variable = time_variable_name.replace("{N}", "").strip()
        new_value_variable = value_variable_name.replace("{N}", "").strip()
        data_dict: Dict[str, Any] = defaultdict(list)
        for index in range:
            time_variable_name_it = time_variable_name.replace("{N}", "{}").format(index)
            value_variable_name_it = value_variable_name.replace("{N}", "{}").format(index)
            if self._dataframe[time_variable_name_it] is not pd.NaT:
                data_dict[new_time_variable].append(self._dataframe[time_variable_name_it])
                data_dict[new_value_variable].append(self._dataframe[value_variable_name_it])

        return pd.DataFrame(data_dict)
