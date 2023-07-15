import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.BoxPlotter import BoxPlotter
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

        st.subheader("Graph options")
        percentage_values = st.checkbox("Are values percentages?", value=True)
        max_value_y_axis = st.checkbox(
            "Set maximum value of y axis to 100%", value=percentage_values
        )
        reference_name = st.text_input(
            "Reference variable name (if any)",
        )
        show_points = st.checkbox("Show points on box plot", value=True)
        st.divider()

        if distribution_variables and categorical_variable:
            assert len(categorical_variable) == 1, "Only one categorical variable allowed"
            st.subheader("Histogram")
            st.plotly_chart(
                StackedHistogram().plot(
                    distribution_variables=distribution_variables,
                    categorical_variable=categorical_variable[0],
                    dataframe=filtered_df,
                    y_max_value=100 if max_value_y_axis else None,
                    reference_variable_name=reference_name,
                    percentage_values=percentage_values,
                )
            )
            st.divider()

        if distribution_variables:
            assert len(categorical_variable) <= 1, "No categorical variable or only one allowed"
            st.subheader("Box plot")
            st.plotly_chart(
                BoxPlotter().plot(
                    distribution_variables=distribution_variables,
                    categorical_variable=categorical_variable[0] if categorical_variable else None,
                    dataframe=filtered_df,
                    show_points=show_points,
                    y_max_value=100 if max_value_y_axis else None,
                    reference_variable_name=reference_name,
                    percentage_values=percentage_values,
                )
            )
            st.divider()
        else:
            st.text("Select variables to analyze :)")
