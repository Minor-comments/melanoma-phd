import logging
import operator
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, cast

import pandas as pd
import scipy.stats as stats

from melanoma_phd.database.statistics.HomogenityTester import HomogenityTester
from melanoma_phd.database.statistics.NormalityTester import NormalityTester
from melanoma_phd.database.statistics.VariableDataframe import VariableDataframe
from melanoma_phd.database.statistics.VariableStatisticalProperties import (
    VariableStatisticalProperties,
)
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable, BooleanVariableConfig
from melanoma_phd.database.variable.BooleanVariableStatic import BooleanVariableStatic
from melanoma_phd.database.variable.CategoricalVariable import (
    CategoricalVariable,
    CategoricalVariableConfig,
)
from melanoma_phd.database.variable.CategoricalVariableStatic import CategoricalVariableStatic
from melanoma_phd.database.variable.IterationCategoricalVariable import IterationCategoricalVariable
from melanoma_phd.database.variable.IterationScalarVariable import IterationScalarVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable, ScalarVariableConfig
from melanoma_phd.database.variable.ScalarVariableStatic import ScalarVariableStatic
from melanoma_phd.database.variable.Variable import PValueType


class IndependencyTestType(Enum):
    PEARSON = "Pearson"
    SPEARMAN = "Spearman"
    T_STUDENT = "T-Student"
    ONE_WAY_ANOVA = "One-Way ANOVA"
    MANNWITHNEYU = "Mann-Whitney U"
    KRUSKAL_WALLIS = "Kruskal-Wallis H-Test"
    FISHER = "Fisher"
    CHI2 = "Chi2"


@dataclass
class IndependenceTestResult:
    variables: Dict[BaseVariable, VariableStatisticalProperties]
    homogeneity: bool
    type: IndependencyTestType
    p_value: PValueType


class IndependenceTester:
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
    ) -> IndependenceTestResult:
        self._check_variables(dataframe, variable, other_variable)
        variable_dataframe_0, variable_dataframe_1 = (
            VariableDataframe(variable=variable, dataframe=dataframe),
            VariableDataframe(variable=other_variable, dataframe=dataframe),
        )
        first_variable_dataframe, second_variable_dataframe = sorted(
            [variable_dataframe_0, variable_dataframe_1]
        )
        first_variable, second_variable = (
            first_variable_dataframe.variable,
            second_variable_dataframe.variable,
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
                first_series, second_series = first_variable_dataframe.merge_and_remove_nulls(
                    second_variable_dataframe
                )
                variable_0_prop.normality = self._normality_tester.test_series(first_series)
                if isinstance(second_variable, ScalarVariable):
                    variable_1_prop.normality = self._normality_tester.test_series(second_series)
                    homogenuos_data = self._homogeneity_tester.test_series(
                        first_series, second_series
                    )
                    if variable_0_prop.normality and variable_1_prop.normality and homogenuos_data:
                        return IndependenceTestResult(
                            variables={
                                first_variable: variable_0_prop,
                                second_variable: variable_1_prop,
                            },
                            homogeneity=homogenuos_data,
                            type=IndependencyTestType.PEARSON,
                            p_value=stats.pearsonr(first_series, second_series).pvalue,
                        )
                    else:
                        return IndependenceTestResult(
                            variables={
                                first_variable: variable_0_prop,
                                second_variable: variable_1_prop,
                            },
                            homogeneity=homogenuos_data,
                            type=IndependencyTestType.SPEARMAN,
                            p_value=stats.spearmanr(first_series, second_series).pvalue,
                        )
                elif isinstance(second_variable, CategoricalVariable):
                    series_by_categories = first_variable.get_data_by_categories(
                        dataframe=dataframe,
                        category_variable=second_variable,
                        remove_nulls=True,
                        remove_short_categories=True,
                    )
                    homogenuos_data = self._homogeneity_tester.test_series(*series_by_categories)
                    if isinstance(second_variable, BooleanVariable):
                        if variable_0_prop.normality and homogenuos_data:
                            return IndependenceTestResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=IndependencyTestType.T_STUDENT,
                                p_value=stats.ttest_ind(*series_by_categories).pvalue,
                            )
                        else:
                            return IndependenceTestResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=IndependencyTestType.MANNWITHNEYU,
                                p_value=stats.mannwhitneyu(*series_by_categories).pvalue,
                            )
                    else:
                        # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                        if variable_0_prop.normality and homogenuos_data:
                            return IndependenceTestResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=IndependencyTestType.ONE_WAY_ANOVA,
                                p_value=stats.f_oneway(*series_by_categories).pvalue,
                            )
                        else:
                            return IndependenceTestResult(
                                variables={
                                    first_variable: variable_0_prop,
                                    second_variable: variable_1_prop,
                                },
                                homogeneity=homogenuos_data,
                                type=IndependencyTestType.KRUSKAL_WALLIS,
                                p_value=stats.kruskal(*series_by_categories).pvalue,
                            )
            elif isinstance(first_variable, CategoricalVariable) and isinstance(
                second_variable, CategoricalVariable
            ):
                # TODO: Differentitate between Ordinal (same as ScalarVariable non-normal) and Nominal (as is here) categorical variables
                serie = first_variable_dataframe.merge_and_remove_nulls(
                    second_variable_dataframe, only_numeric=True
                )
                table = stats.contingency.crosstab(*serie).count
                if table.size < 2:
                    table.resize([2, 2], refcheck=False)
                if isinstance(first_variable, BooleanVariable) and isinstance(
                    second_variable, BooleanVariable
                ):
                    return IndependenceTestResult(
                        variables={
                            first_variable: variable_0_prop,
                            second_variable: variable_1_prop,
                        },
                        homogeneity=False,
                        type=IndependencyTestType.FISHER,
                        p_value=stats.fisher_exact(table).pvalue,
                    )
                return IndependenceTestResult(
                    variables={
                        first_variable: variable_0_prop,
                        second_variable: variable_1_prop,
                    },
                    homogeneity=False,
                    type=IndependencyTestType.CHI2,
                    p_value=stats.chi2_contingency(table).pvalue,
                )
        except ValueError as e:
            raise ValueError(
                f"Independence test could not be done for `{variable.name}` ({variable.__class__.__name__}) and `{other_variable.name}` ({other_variable.__class__.__name__}) due to: {e}"
            )

        raise ValueError(
            f"Combination of `{variable.__class__.__name__}` and `{other_variable.__class__.__name__}` variable types is not supported"
        )

    def table(self, dataframe: pd.DataFrame, variables: List[BaseVariable]) -> pd.DataFrame:
        self._check_variables(dataframe, *variables)
        results: List[List[IndependenceTestResult]] = []
        columns: List[str] = []
        index: List[str] = []
        for v1 in variables:
            v1_results = [self.test(dataframe, v1, v2) for v2 in variables]
            results.append(v1_results)
            var_title = f"{v1.name} [{v1_results[-1].variables[v1].type.value}] Normality={v1_results[-1].variables[v1].normality}"
            columns.append(var_title)
            index.append(var_title)
        return pd.DataFrame(
            data=[
                [
                    f"{result.p_value:.4f} (Homogeneity={result.homogeneity}, {result.type.value})"
                    for result in result_row
                ]
                for result_row in results
            ],
            columns=columns,
            index=index,
        )

    def test_two_population(
        self, dataframe_0: pd.DataFrame, dataframe_1: pd.DataFrame, variable: BaseVariable
    ) -> IndependenceTestResult:
        return self._test_two_population(
            dataframe_0=dataframe_0, dataframe_1=dataframe_1, variable=variable
        )[0]

    def _test_two_population(
        self, dataframe_0: pd.DataFrame, dataframe_1: pd.DataFrame, variable: BaseVariable
    ) -> Tuple[IndependenceTestResult, BaseVariable, BooleanVariableStatic]:
        variable_dataframe_0 = VariableDataframe(variable, dataframe_0)
        variable_dataframe_1 = VariableDataframe(variable, dataframe_1)
        value_series = pd.concat(
            [
                variable_dataframe_0.get_series(only_numeric=True),
                variable_dataframe_1.get_series(only_numeric=True),
            ],
            ignore_index=True,
        )
        group_series = pd.concat(
            [pd.Series([0] * len(dataframe_0)), pd.Series([1] * len(dataframe_1))],
            ignore_index=True,
        )
        dataframe = pd.DataFrame(
            {variable.id: value_series.values, "group": group_series.values},
            columns=[variable.id, "group"],
        )
        reference_variable = variable
        if isinstance(variable, IterationScalarVariable):
            reference_variable = ScalarVariableStatic(
                ScalarVariableConfig(id=variable.id, name=variable.name, selectable=False)
            )
            reference_variable.init_from_dataframe(dataframe=variable_dataframe_0.dataframe)
        elif isinstance(variable, IterationCategoricalVariable):
            categories = {
                key: value
                for key, value in zip(
                    cast(IterationCategoricalVariable, variable).category_names,
                    cast(IterationCategoricalVariable, variable).category_values,
                )
            }
            reference_variable = CategoricalVariableStatic(
                CategoricalVariableConfig(
                    id=variable.id,
                    name=variable.name,
                    selectable=False,
                    categories=categories,
                )
            )
            reference_variable.init_from_dataframe(dataframe=variable_dataframe_0.dataframe)

        group_variable = BooleanVariableStatic(
            BooleanVariableConfig(
                id="group",
                name="group",
                selectable=False,
                categories={0: "No", 1: "Yes"},
            )
        )
        group_variable.init_from_dataframe(dataframe=dataframe)
        return (
            self.test(dataframe, reference_variable, group_variable),
            reference_variable,
            group_variable,
        )

    def table_two_population(
        self, dataframe_0: pd.DataFrame, dataframe_1: pd.DataFrame, variables: List[BaseVariable]
    ) -> pd.DataFrame:
        self._check_variables(dataframe_0, *variables)
        self._check_variables(dataframe_1, *variables)
        results: List[IndependenceTestResult] = []
        columns: List[str] = []
        index: List[str] = []

        columns.append(f"{dataframe_0.name} vs {dataframe_1.name} p value")
        for variable in variables:
            test_result, reference_variable, _ = self._test_two_population(
                dataframe_0, dataframe_1, variable
            )
            results.append(test_result)
            var_title_index = f"{variable.id} [{test_result.variables[reference_variable].type.value}] Normality={test_result.variables[reference_variable].normality}"
            index.append(var_title_index)
        return pd.DataFrame(
            data=[
                f"{result.p_value:.4f} (Homogeneity={result.homogeneity}, {result.type.value})"
                for result in results
            ],
            columns=columns,
            index=index,
        )

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
