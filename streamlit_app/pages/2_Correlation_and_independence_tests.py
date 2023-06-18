import os
import sys

import streamlit as st

from melanoma_phd.visualizer.StackedHistogram import StackedHistogram

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from melanoma_phd.database.Correlationer import (
    Correlationer,
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.IndependenceTester import IndependenceTester
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database,
    select_filters,
    select_variables,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Correlation and Independence Tests")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        df_result = filter_database(app=app, filters=filters)

        st.subheader("Variable selection")
        selected_variables = select_variables(
            app,
            SelectVariableConfig(
                "Correlation and Independence analysis",
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
            independence_table = independence_tester.table(df_result, selected_variables)
            st.dataframe(independence_table)

            st.header("Correlation")
            correlationer = Correlationer(
                normality_null_hypothesis=normality_null_hypothesis,
                homogeneity_null_hypothesis=homogeneity_null_hypothesis,
            )
            correlation_table = correlationer.table(df_result, selected_variables)
            st.dataframe(correlation_table)
        else:
            st.text("Select variables to analyze :)")
