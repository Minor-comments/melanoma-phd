import os
import sys

import streamlit as st

from melanoma_phd.visualizer.StackedHistogram import StackedHistogram

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database,
    select_filters,
    select_several_variables,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Distributions over categories")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        df_result = filter_database(app=app, filters=filters)

        st.subheader("Variable selection")
        distribution_variables, categorical_variable = select_several_variables(
            app,
            SelectVariableConfig(
                "Distribution variables",
                variable_types=[
                    ScalarVariable,
                ],
                displayed_title="Distribution variables to select",
            ),
            SelectVariableConfig(
                "Categorical variables",
                variable_types=[
                    CategoricalVariable,
                ],
                displayed_title="Categorical variables to select",
            ),
        )

        if distribution_variables and categorical_variable:
            assert len(categorical_variable) == 1, "Only one categorical variable allowed"
            categorical_variable = categorical_variable[0]

            st.plotly_chart(
                StackedHistogram().plot(
                    distribution_variables=distribution_variables,
                    categorical_variable=categorical_variable,
                    dataframe=df_result,
                )
            )
        else:
            st.text("Select variables to analyze :)")
