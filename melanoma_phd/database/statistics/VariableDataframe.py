from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


@dataclass
class VariableDataframe:
    variable: BaseVariable
    dataframe: pd.DataFrame

    @property
    def id(self) -> str:
        return (
            f"{self.dataframe.name}.{self.variable.id}"
            if hasattr(self.dataframe, "name")
            else f"{self.variable.id}"
        )

    def __lt__(self, other: VariableDataframe) -> bool:
        type_order = [ScalarVariable, BooleanVariable, CategoricalVariable]
        for var_type in type_order:
            if isinstance(self.variable, var_type):
                return True
            elif isinstance(other.variable, var_type):
                return False
        return False

    def is_paired_dataframe_with(self, other: VariableDataframe) -> bool:
        series_0 = self.get_series()
        series_1 = other.get_series()
        return series_0.size == series_1.size and (
            all(np.equal(series_0.index.values, series_1.index.values))
        )

    def is_series_empty(self) -> bool:
        serie = self.get_series()
        null_mask = serie.isnull()
        return sum(null_mask) == len(null_mask)

    def get_series_from_df(self, dataframe: pd.DataFrame, only_numeric: bool = False) -> pd.Series:
        if only_numeric:
            if isinstance(self.variable, CategoricalVariable):
                return self.variable.get_numeric_series(dataframe)
            else:
                logging.warning(
                    f"Trying to get numeric series for `{self.variable.name}` ({self.variable.__class__.__name__}) but it is not a categorical variable, defaulting to get_series"
                )
        return self.variable.get_series(dataframe)

    def get_series(self, only_numeric: bool = False) -> pd.Series:
        return self.get_series_from_df(dataframe=self.dataframe, only_numeric=only_numeric)

    def merge_and_remove_nulls(
        self, other: VariableDataframe, only_numeric: bool = False
    ) -> Tuple[pd.Series, ...]:
        serie = self.get_series(only_numeric=only_numeric)
        other_serie = other.get_series(only_numeric=only_numeric)
        null_mask = serie.isnull() | other_serie.isnull()
        if sum(null_mask):
            logging.info(
                f"{self.__class__.__name__}: {sum(null_mask)} nulls removed out of {len(null_mask)} values from variables {[variable.name for variable in [self.variable, other.variable]]}"
            )
        return tuple(serie[~null_mask] for serie in [serie, other_serie])
