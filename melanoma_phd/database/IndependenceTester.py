from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.HomogenityTester import HomogenityTester
from melanoma_phd.database.NormalityTester import NormalityTester
from melanoma_phd.database.variable.BaseVariable import BaseVariable, PValueType
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class IndependenceTester:
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

    def test(
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
                        return stats.pearsonr(first_series, second_series).pvalue
                    else:
                        return stats.spearmanr(first_series, second_series).pvalue
                elif isinstance(second_variable, CategoricalVariable):
                    series_by_categories = first_variable.get_data_by_categories(
                        dataframe=dataframe, category_variable=second_variable, remove_nulls=True
                    )
                    homogenuos_data = self._homogeneity_tester.test(*series_by_categories)
                    if isinstance(second_variable, BooleanVariable):
                        if normal_data and homogenuos_data:
                            return stats.ttest_ind(*series_by_categories).pvalue
                        else:
                            return stats.mannwhitneyu(*series_by_categories).pvalue
                    else:
                        # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                        if normal_data and homogenuos_data:
                            return stats.f_oneway(*series_by_categories).pvalue
                        else:
                            return stats.kruskal(*series_by_categories).pvalue
            elif isinstance(first_variable, CategoricalVariable) and isinstance(
                second_variable, CategoricalVariable
            ):
                # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                table = stats.contingency.crosstab(
                    *self._remove_nulls_from_any_serie_to_all(
                        first_variable.get_numeric_series(dataframe),
                        second_variable.get_numeric_series(dataframe),
                    )
                ).count
                if isinstance(first_variable, BooleanVariable) and isinstance(
                    second_variable, BooleanVariable
                ):
                    return stats.fisher_exact(table).pvalue
                return stats.chi2_contingency(table).pvalue
        except ValueError as e:
            raise ValueError(
                f"Independence test could not be done for `{variable.name}` and `{other_variable.name}` due to: {e}"
            )

        raise ValueError(
            f"Combination of `{variable.__class__.__name__}` and `{other_variable.__class__.__name__}` variable types is not supported"
        )

    def table(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> pd.DataFrame:
        return pd.DataFrame(
            [[self.test(dataframe, v1, v2) for v2 in variables] for v1 in variables],
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
