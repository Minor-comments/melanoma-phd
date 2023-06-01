from typing import Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.variable.BaseVariable import PValue
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class NormalityTester:
    def __init__(self, null_hypothesis: PValue = 0.05) -> None:
        self._null_hypothesis = null_hypothesis

    def test_series(self, series: pd.Series) -> bool:
        try:
            return stats.shapiro(series).pvalue >= self._null_hypothesis
        except ValueError as e:
            raise ValueError(f"Normality test failed due to: {e}")

    def test_many_series(self, *series: pd.Series) -> bool:
        return all(self.test_series(serie) for serie in series)

    def test_variable(self, data: Union[pd.DataFrame, pd.Series], variable: ScalarVariable) -> bool:
        series = variable._get_non_na_data(data=data)
        try:
            return self.test_series(series)
        except ValueError as e:
            raise ValueError(f"Variable '{variable.name}': {e}")

    def test_variables(self, data: pd.DataFrame, *variables: ScalarVariable) -> bool:
        return all(self.test_variable(data, variable=variable) for variable in variables)
