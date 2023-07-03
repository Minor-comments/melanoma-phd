from typing import Any, List, Optional, Tuple, Union

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.HomogenityTester import HomogenityTester
from melanoma_phd.database.NormalityTester import NormalityTester
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.Variable import PValueType
from melanoma_phd.logger.StreamlitLogger import StreamlitLogger


class IndependenceTester(StreamlitLogger):
    def __init__(
        self,
        normality_null_hypothesis: PValueType = 0.05,
        homogeneity_null_hypothesis: PValueType = 0.05,
    ) -> None:
        super().__init__()
        self._normality_tester = NormalityTester(null_hypothesis=normality_null_hypothesis)
        self._homogeneity_tester = HomogenityTester(
            null_hypothesis=homogeneity_null_hypothesis,
            normality_null_hypothesis=normality_null_hypothesis,
        )

    def test(
        self, dataframe: pd.DataFrame, variable: BaseVariable, other_variable: BaseVariable
    ) -> PValueType:
        self._check_variables(dataframe, variable, other_variable)
        first_variable, second_variable = self._order_variables(variable, other_variable)
        first_variable.init_from_dataframe(dataframe=dataframe)
        second_variable.init_from_dataframe(dataframe=dataframe)
        first_series, second_series = self._remove_nulls_from_any_serie_to_all(
            dataframe, first_variable, second_variable
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
                        dataframe=dataframe,
                        category_variable=second_variable,
                        remove_nulls=True,
                        remove_short_categories=True,
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
                        dataframe, first_variable, second_variable, only_numeric=True
                    )
                ).count
                if isinstance(first_variable, BooleanVariable) and isinstance(
                    second_variable, BooleanVariable
                ):
                    return stats.fisher_exact(table).pvalue
                return stats.chi2_contingency(table).pvalue
        except ValueError as e:
            raise ValueError(
                f"Independence test could not be done for `{variable.name}` ({variable.__class__.__name__}) and `{other_variable.name}` ({other_variable.__class__.__name__}) due to: {e}"
            )

        raise ValueError(
            f"Combination of `{variable.__class__.__name__}` and `{other_variable.__class__.__name__}` variable types is not supported"
        )

    def table(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> pd.DataFrame:
        self._check_variables(dataframe, *variables)
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

    def _check_variables(self, dataframe: pd.DataFrame, *variables: BaseVariable):
        empty_variables = []
        for variable in variables:
            serie = variable.get_series(dataframe)
            null_mask = serie.isnull()
            if sum(null_mask) == len(null_mask):
                empty_variables.append(variable)
        if empty_variables:
            error_msg = f"{self.__class__.__name__}: variables {[variable.name for variable in empty_variables]} are empty for the given filters. Please review database or filters."
            self.error(error_msg)
            raise ValueError(error_msg)

    def _remove_nulls_from_any_serie_to_all(
        self, dataframe: pd.DataFrame, *variables: BaseVariable, only_numeric: bool = False
    ) -> Tuple[pd.Series, ...]:
        series = []
        serie = self.__get_data(variables[0], dataframe, only_numeric=only_numeric)
        series.append(serie)
        index = serie.index.values
        null_mask = serie.isnull()
        for variable in variables[1:]:
            serie = self.__get_data(variable, dataframe, only_numeric=only_numeric)
            assert all(serie.index.values == index), "Indexes of all series must be the same"
            series.append(serie)
            null_mask |= serie.isnull()
        if sum(null_mask):
            self.info(
                f"{self.__class__.__name__}: {sum(null_mask)} nulls removed out of {len(null_mask)} values from variables {[variable.name for variable in variables]}"
            )
        return tuple(serie[~null_mask] for serie in series)

    def __get_data(
        self, variable: BaseVariable, dataframe: pd.DataFrame, only_numeric: bool = False
    ) -> pd.Series:
        if only_numeric:
            if isinstance(variable, CategoricalVariable):
                return variable.get_numeric_series(dataframe)
            else:
                self.warning(
                    f"Trying to get numeric series for `{variable.name}` ({variable.__class__.__name__}) but it is not a categorical variable, defaulting to get_series"
                )
        return variable.get_series(dataframe)
