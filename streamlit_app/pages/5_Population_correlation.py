import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)  # isort: skip
from melanoma_phd.database.statistics.IndependenceTester import IndependenceTester
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.BoxPlotter import BoxPlotter
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    select_population_section,
    select_variables_by_checkbox,
)

if __name__ == "__main__":
    st.title("Population correlation")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        with st.expander("Population 1"):
            db_view_1 = select_population_section("Population 1", database)

        with st.expander("Population 2"):
            db_view_2 = select_population_section("Population 2", database)

        st.subheader("Variable selection to correlate")
        selected_variables = select_variables_by_checkbox(
            database=database,
            select_variable_config=SelectVariableConfig(
                variable_selection_name="Correlation and Independence analysis of populations",
                unique_form_title="Variables to analyze from populations",
                variable_types=[
                    ScalarVariable,
                    CategoricalVariable,
                    BooleanVariable,
                ],
            ),
        )
        normality_null_hypothesis = st.number_input(
            "Normality null hypotesis", min_value=0.0, max_value=1.0, step=0.01, value=0.05
        )
        homogeneity_null_hypothesis = st.number_input(
            "Homogeneity null hypotesis", min_value=0.0, max_value=1.0, step=0.01, value=0.05
        )
        if selected_variables:
            st.header("Independence Tests (p-value)")
            independence_tester = IndependenceTester(
                normality_null_hypothesis=normality_null_hypothesis,
                homogeneity_null_hypothesis=homogeneity_null_hypothesis,
            )
            independence_table = independence_tester.table_two_population(
                dataframe_0=db_view_1.dataframe,
                dataframe_1=db_view_2.dataframe,
                variables=selected_variables,
            )
            st.dataframe(independence_table)
            scalar_variables = [
                variable for variable in selected_variables if isinstance(variable, ScalarVariable)
            ]
            for scalar_variable in scalar_variables:
                (
                    dataframe,
                    reference_variable,
                    group_variable,
                ) = independence_tester.create_two_population_dataframe(
                    dataframe_0=db_view_1.dataframe,
                    dataframe_1=db_view_2.dataframe,
                    variable=scalar_variable,
                )
                st.subheader(f"{scalar_variable.name} box plot")
                st.plotly_chart(
                    BoxPlotter().plot(
                        distribution_variables=[reference_variable],
                        dataframe=dataframe,
                        categorical_variable=group_variable,
                    )
                )
        else:
            st.text("Select variables to analyze :)")
