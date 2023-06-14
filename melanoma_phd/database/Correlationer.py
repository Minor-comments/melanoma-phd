from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import scipy.stats as stats
import statsmodels.api as sa
import statsmodels.formula.api as sfa
from dython.nominal import theils_u
from sklearn.metrics import matthews_corrcoef

from melanoma_phd.database.HomogenityTester import HomogenityTester
from melanoma_phd.database.NormalityTester import NormalityTester
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.Variable import PValueType


class Correlationer:
    def __init__(
        self,
        normality_null_hypothesis: PValueType = 0.05,
        homogeneity_null_hypothesis: PValueType = 0.05,
    ) -> None:
        self._normality_tester = NormalityTester(null_hypothesis=normality_null_hypothesis)
        self._homogeneity_tester = HomogenityTester(
            null_hypothesis=homogeneity_null_hypothesis,
            normality_null_hypothesis=normality_null_hypothesis,
        )

    def correlate(
        self, dataframe: pd.DataFrame, variable: BaseVariable, other_variable: BaseVariable
    ) -> PValueType:
        first_variable, second_variable = self._order_variables(variable, other_variable)
        first_variable.init_from_dataframe(dataframe=dataframe)
        second_variable.init_from_dataframe(dataframe=dataframe)
        first_series, second_series = self._remove_nulls_from_any_serie_to_all(
            first_variable.get_series(dataframe), second_variable.get_series(dataframe)
        )
        try:
            if isinstance(first_variable, ScalarVariable):
                normal_data = self._normality_tester.test_series(first_series)
                if isinstance(second_variable, ScalarVariable):
                    normal_data = normal_data and self._normality_tester.test_series(second_series)
                    homogenuos_data = self._homogeneity_tester.test(first_series, second_series)
                    if normal_data and homogenuos_data:
                        return stats.pearsonr(first_series, second_series).statistic
                    else:
                        return stats.spearmanr(first_series, second_series).statistic
                elif isinstance(second_variable, CategoricalVariable):
                    if isinstance(second_variable, BooleanVariable):
                        return stats.pointbiserialr(
                            first_series, CategoricalVariable.get_numeric(second_series)
                        ).statistic
                    else:
                        # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                        series_by_categories = first_variable.get_data_by_categories(
                            dataframe=dataframe,
                            category_variable=second_variable,
                            remove_nulls=True,
                        )
                        homogenuos_data = self._homogeneity_tester.test(*series_by_categories)
                        if normal_data and homogenuos_data:
                            return self._calculate_omega_square(
                                continuous_series=first_series, categorical_series=second_series
                            )
                        else:
                            return self._calculate_epsilon_squared(
                                h_statistic=stats.kruskal(*series_by_categories).statistic,
                                n=len(first_series),
                            )
            elif isinstance(first_variable, BooleanVariable) and isinstance(
                second_variable, CategoricalVariable
            ):
                if isinstance(second_variable, BooleanVariable):
                    return matthews_corrcoef(first_series, second_series)
                elif isinstance(second_variable, CategoricalVariable):
                    # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                    # Using directly `variable` and `other_variable` due to the asymmetry of Theil's U calculation
                    return theils_u(
                        *self._remove_nulls_from_any_serie_to_all(
                            variable.get_series(dataframe),
                            other_variable.get_series(dataframe),
                        )
                    )
            if isinstance(first_variable, CategoricalVariable):
                # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                if isinstance(second_variable, CategoricalVariable):
                    # Using directly `variable` and `other_variable` due to the asymmetry of Theil's U calculation
                    return theils_u(
                        *self._remove_nulls_from_any_serie_to_all(
                            variable.get_series(dataframe),
                            other_variable.get_series(dataframe),
                        )
                    )
        except ValueError as e:
            raise ValueError(
                f"Independence test could not be done for `{variable.name}` and `{other_variable.name}` due to: {e}"
            )

        raise ValueError(
            f"Combination of `{variable.__class__.__name__}` and `{other_variable.__class__.__name__}` variable types is not supported"
        )

    def table(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> pd.DataFrame:
        return pd.DataFrame(
            [[self.correlate(dataframe, v1, v2) for v2 in variables] for v1 in variables],
            columns=[v.name for v in variables],
            index=[v.name for v in variables],
        )

    def _order_variables(self, *variables: BaseVariable) -> Tuple[BaseVariable, ...]:
        already_ordered_index = set()
        ordered_variables = []
        for variable_type in [ScalarVariable, BooleanVariable, CategoricalVariable]:
            for i, variable in enumerate(variables):
                if i in already_ordered_index:
                    continue

                if isinstance(variable, variable_type):
                    ordered_variables.append(variable)
                    already_ordered_index.add(i)

            if len(variables) == len(ordered_variables):
                break
        return tuple(ordered_variables)

    def _remove_nulls_from_any_serie_to_all(self, *series: pd.Series) -> Tuple[pd.Series, ...]:
        index = series[0].index.values
        null_mask = series[0].isnull()
        for serie in series[1:]:
            assert all(serie.index.values == index), "Indexes of all series must be the same"
            null_mask |= serie.isnull()
        return tuple(serie[~null_mask] for serie in series)

    def _calculate_omega_square(self, continuous_series: pd.Series, categorical_series: pd.Series):
        anova = self._calculate_anova(
            continuous_series=continuous_series, categorical_series=categorical_series
        )
        omega_square = (anova[:-1]["sum_sq"] - (anova[:-1]["df"] * anova["mean_sq"][-1])) / (
            sum(anova["sum_sq"]) + anova["mean_sq"][-1]
        )
        return omega_square.values[0]

    def _calculate_anova(
        self, continuous_series: pd.Series, categorical_series: pd.Series
    ) -> Optional[pd.DataFrame]:
        df = pd.DataFrame(
            {"Continuous": continuous_series.values, "Categorical": categorical_series.values},
        )
        lm = sfa.ols("Continuous ~ C(Categorical)", data=df).fit()
        return sa.stats.anova_lm(lm)

    def _calculate_epsilon_squared(self, h_statistic: float, n: int) -> float:
        return h_statistic * (n + 1) / (n**2 - 1)
