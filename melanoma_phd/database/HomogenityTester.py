from typing import Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.NormalityTester import NormalityTester
from melanoma_phd.database.variable.BaseVariable import PValue
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class HomogenityTester:
    def __init__(
        self, null_hypothesis: PValue = 0.05, normality_null_hypothesis: PValue = 0.05
    ) -> None:
        self._null_hypothesis = null_hypothesis
        self._normality_tester = NormalityTester(normality_null_hypothesis)

    def test(self, *series: pd.Series) -> PValue:
        if self._normality_tester.test_many_series(*series):
            return stats.bartlett(*series).pvalue >= self._null_hypothesis
        else:
            return stats.levene(*series).pvalue >= self._null_hypothesis

    def test_variable(self, data: Union[pd.DataFrame, pd.Series], variable: ScalarVariable) -> bool:
        series = variable._get_non_na_data(data=data)
        return self.test(series)

    def test_variables(self, data: pd.DataFrame, *variables: ScalarVariable) -> bool:
        return all(self.test_variable(data, variable=variable) for variable in variables)
    
    def test_scalar_with_categorical_variables(self, data: pd.DataFrame, scalar_variable: ScalarVariable, categorical_variable: CategoricalVariable) -> bool:
        series_by_categories = scalar_variable._get_data_by_categories(
            dataframe=data, category_variable=categorical_variable
        )
        return self.test(*series_by_categories)