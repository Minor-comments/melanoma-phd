import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.StackedHistogram import StackedHistogram
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database,
    select_filters,
    select_several_variables_by_checkbox,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Distributions over categories")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        filters = select_filters(database)
        db_view = filter_database(database=database, filters=filters)
        filtered_df = db_view.dataframe

        st.subheader("Variable selection")
        distribution_variables, categorical_variable = select_several_variables_by_checkbox(
            database,
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
                    dataframe=filtered_df,
                )
            )
        else:
            st.text("Select variables to analyze :)")
