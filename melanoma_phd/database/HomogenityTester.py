from typing import Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.NormalityTester import NormalityTester
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.Variable import PValueType


class HomogenityTester:
    def __init__(
        self, null_hypothesis: PValueType = 0.05, normality_null_hypothesis: PValueType = 0.05
    ) -> None:
        self._null_hypothesis = null_hypothesis
        self._normality_tester = NormalityTester(normality_null_hypothesis)

    def test(self, *series: pd.Series) -> bool:
        if self._normality_tester.test_many_series(*series):
            homogenity_test = stats.bartlett
        else:
            homogenity_test = stats.levene
        try:
            return homogenity_test(*series).pvalue >= self._null_hypothesis
        except ValueError as e:
            raise ValueError(f"Homogenity test failed due to: {e}")

    def test_variable(self, data: Union[pd.DataFrame, pd.Series], variable: ScalarVariable) -> bool:
        series = variable.get_non_na_series(data=data)
        try:
            return self.test(series)
        except ValueError as e:
            raise ValueError(f"Variable '{variable.name}': {e}")

    def test_variables(self, data: pd.DataFrame, *variables: ScalarVariable) -> bool:
        return all(self.test_variable(data, variable=variable) for variable in variables)

    def test_scalar_with_categorical_variables(
        self,
        data: pd.DataFrame,
        scalar_variable: ScalarVariable,
        categorical_variable: CategoricalVariable,
    ) -> bool:
        series_by_categories = scalar_variable.get_data_by_categories(
            dataframe=data,
            category_variable=categorical_variable,
            remove_nulls=True,
            remove_short_categories=True,
        )
        return self.test(*series_by_categories)
