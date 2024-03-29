import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # isort: skip
from melanoma_phd.database.statistics.Correlationer import Correlationer
from melanoma_phd.database.statistics.IndependenceTester import IndependenceTester
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database_section,
    select_filters_sidebar,
    select_variables_by_checkbox,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Correlation and Independence Tests")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        filters = select_filters_sidebar(database)
        db_view = filter_database_section(database=database, filters=filters)
        filtered_df = db_view.dataframe

        st.subheader("Variable selection")
        selected_variables = select_variables_by_checkbox(
            database=database,
            select_variable_config=SelectVariableConfig(
                variable_selection_name="Correlation and Independence analysis",
                unique_form_title="Variables to analyze",
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
            independence_table, errors = independence_tester.table(filtered_df, selected_variables)
            for error in errors:
                st.error(error)
            st.dataframe(independence_table)

            st.header("Correlation")
            correlationer = Correlationer(
                normality_null_hypothesis=normality_null_hypothesis,
                homogeneity_null_hypothesis=homogeneity_null_hypothesis,
            )
            correlation_table, errors = correlationer.table(filtered_df, selected_variables)
            for error in errors:
                st.error(error)
            st.dataframe(correlation_table)
        else:
            st.text("Select variables to analyze :)")
