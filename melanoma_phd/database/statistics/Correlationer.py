import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pandas as pd
import scipy.stats as stats
import statsmodels.api as sa
import statsmodels.formula.api as sfa
from dython.nominal import theils_u
from sklearn.metrics import matthews_corrcoef

from melanoma_phd.database.statistics.HomogenityTester import HomogenityTester
from melanoma_phd.database.statistics.NormalityTester import NormalityTester
from melanoma_phd.database.statistics.VariableStatisticalProperties import \
    VariableStatisticalProperties
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.Variable import PValueType


class CorrelationTestType(Enum):
    PEARSON = "Pearson"
    SPEARMAN = "Spearman"
    POINT_BISERIAL = "Point biserial"
    OMEGA_SQUARED = "omega squared (ANOVA)"
    EPSILON_SQUARED = "epsilon squared (Kruskal-Wallis H)"
    MATTHEWS_CORRELATION_COEFFICIENT = "Matthews correlation coefficient"
    THEILS_U = "Theil's U"


@dataclass
class CorrelationResult:
    variables: Dict[BaseVariable, VariableStatisticalProperties]
    homogeneity: bool
    type: CorrelationTestType
    coefficient: PValueType


class Correlationer:
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

    def correlate(
        self, dataframe: pd.DataFrame, variable: BaseVariable, other_variable: BaseVariable
    ) -> CorrelationResult:
        self._check_variables(dataframe, variable, other_variable)
        first_variable, second_variable = self._order_variables(variable, other_variable)
        first_variable.init_from_dataframe(dataframe=dataframe)
        second_variable.init_from_dataframe(dataframe=dataframe)
        first_series, second_series = self._remove_nulls_from_any_serie_to_all(
            dataframe, first_variable, second_variable
        )
        variable_0_prop = VariableStatisticalProperties(
            type=first_variable.statistical_type(),
            normality=False,
        )
        variable_1_prop = VariableStatisticalProperties(
            type=second_variable.statistical_type(),
            normality=False,
        )
        try:
            if isinstance(first_variable, ScalarVariable):
                variable_0_prop.normality = self._normality_tester.test_series(first_series)
                if isinstance(second_variable, ScalarVariable):
                    variable_1_prop.normality = self._normality_tester.test_series(second_series)
                    homogenuos_data = self._homogeneity_tester.test_series(
                        first_series, second_series
                    )
                    if variable_0_prop.normality and variable_1_prop.normality and homogenuos_data:
                        return CorrelationResult(
                            variables={
                                first_variable: variable_0_prop,
                                second_variable: variable_1_prop,
                            },
                            homogeneity=homogenuos_data,
                            type=CorrelationTestType.PEARSON,
                            coefficient=stats.pearsonr(first_series, second_series).statistic,
                        )
                    else:
                        return CorrelationResult(
                            variables={
                                first_variable: variable_0_prop,
                                second_variable: variable_1_prop,
                            },
                            homogeneity=homogenuos_data,
                            type=CorrelationTestType.SPEARMAN,
                            coefficient=stats.spearmanr(first_series, second_series).statistic,
                        )
                elif isinstance(second_variable, CategoricalVariable):
                    if isinstance(second_variable, BooleanVariable):
                        return CorrelationResult(
                            variables={
                                first_variable: variable_0_prop,
                                second_variable: variable_1_prop,
                            },
                            homogeneity=False,
                            type=CorrelationTestType.POINT_BISERIAL,
                            coefficient=stats.pointbiserialr(
                                first_series, CategoricalVariable.get_numeric(second_series)
                            ).statistic,
                        )
                    else:
                        # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                        series_by_categories = first_variable.get_data_by_categories(
                            dataframe=dataframe,
                            category_variable=second_variable,
                            remove_nulls=True,
                            remove_short_categories=True,
                        )
                        homogenuos_data = self._homogeneity_tester.test_series(
                            *series_by_categories
                        )
                        if variable_0_prop.normality and homogenuos_data:
                            return CorrelationResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=CorrelationTestType.OMEGA_SQUARED,
                                coefficient=self._calculate_omega_square(
                                    continuous_series=first_series, categorical_series=second_series
                                ),
                            )
                        else:
                            return CorrelationResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=CorrelationTestType.EPSILON_SQUARED,
                                coefficient=self._calculate_epsilon_squared(
                                    h_statistic=stats.kruskal(*series_by_categories).statistic,
                                    n=len(first_series),
                                ),
                            )
            elif isinstance(first_variable, BooleanVariable) and isinstance(
                second_variable, CategoricalVariable
            ):
                if isinstance(second_variable, BooleanVariable):
                    return CorrelationResult(
                        variables={
                            first_variable: variable_0_prop,
                            second_variable: variable_1_prop,
                        },
                        homogeneity=False,
                        type=CorrelationTestType.MATTHEWS_CORRELATION_COEFFICIENT,
                        coefficient=matthews_corrcoef(first_series, second_series),
                    )
                elif isinstance(second_variable, CategoricalVariable):
                    # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                    # Using directly `variable` and `other_variable` due to the asymmetry of Theil's U calculation
                    return CorrelationResult(
                        variables={
                            first_variable: variable_0_prop,
                            second_variable: variable_1_prop,
                        },
                        homogeneity=False,
                        type=CorrelationTestType.THEILS_U,
                        coefficient=theils_u(
                            *self._remove_nulls_from_any_serie_to_all(
                                dataframe, variable, other_variable
                            )
                        ),
                    )
            elif isinstance(first_variable, CategoricalVariable):
                # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                if isinstance(second_variable, CategoricalVariable):
                    # Using directly `variable` and `other_variable` due to the asymmetry of Theil's U calculation
                    return CorrelationResult(
                        variables={
                            first_variable: variable_0_prop,
                            second_variable: variable_1_prop,
                        },
                        homogeneity=False,
                        type=CorrelationTestType.THEILS_U,
                        coefficient=theils_u(
                            *self._remove_nulls_from_any_serie_to_all(
                                dataframe, variable, other_variable
                            )
                        ),
                    )
        except ValueError as e:
            raise ValueError(
                f"Independence test could not be done for `{variable.name}` and `{other_variable.name}` due to: {e}"
            )

        raise ValueError(
            f"Combination of `{variable.__class__.__name__}` and `{other_variable.__class__.__name__}` variable types is not supported"
        )

    def table(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> pd.DataFrame:
        self._check_variables(dataframe, *variables)
        results: List[List[CorrelationResult]] = []
        columns: List[str] = []
        index: List[str] = []
        for v1 in variables:
            v1_results = [self.correlate(dataframe, v1, v2) for v2 in variables]
            results.append(v1_results)
            var_title = f"{v1.name} [{v1_results[-1].variables[v1].type.value}] Normality={v1_results[-1].variables[v1].normality}"
            columns.append(var_title)
            index.append(var_title)
        return pd.DataFrame(
            data=[
                [
                    f"{result.coefficient:.4f} (Homogeneity={result.homogeneity}, {result.type.value})"
                    for result in result_row
                ]
                for result_row in results
            ],
            columns=columns,
            index=index,
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
            logging.error(error_msg)
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
            logging.info(
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
                logging.warning(
                    f"Trying to get numeric series for `{variable.name}` ({variable.__class__.__name__}) but it is not a categorical variable, defaulting to get_series"
                )
        return variable.get_series(dataframe)

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