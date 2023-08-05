import os
import sys

import streamlit as st

from melanoma_phd.database.variable.RemainingDistributionVariable import (
    RemainingDistributionVariable,
    RemainingDistributionVariableConfig,
)
from melanoma_phd.visualizer.ColorGenerator import ColorGenerator
from melanoma_phd.visualizer.PlotlyAxisUpdater import PlotlyAxisUpdaterConfig

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # isort: skip
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
        enable_max_value_y_axis = st.checkbox(
            "Enable set maximum value of y axis", value=percentage_values
        )
        max_value_y_axis = st.number_input(
            "Maximum value of y axis", value=100, disabled=not enable_max_value_y_axis
        )
        total_distribution_sum = st.number_input("Total distribution sum", value=100)
        reference_name = st.text_input(
            "Reference variable name (if any)",
            help="Leave empty if no remaining reference variable is desired",
        )
        remaining_distribution_variable_name = st.text_input(
            "Remaining distribution variable name (if any)",
            help="Leave empty if no remaining distribution variable is desired",
        )
        show_points = st.checkbox("Show points on box plot", value=True)
        st.divider()

        if remaining_distribution_variable_name:
            distribution_variables.append(
                RemainingDistributionVariable(
                    config=RemainingDistributionVariableConfig(
                        id=remaining_distribution_variable_name,
                        name=remaining_distribution_variable_name,
                        distribution_variables=distribution_variables,
                        total_distribution_sum=total_distribution_sum,
                    )
                )
            )

        if distribution_variables and categorical_variable:
            assert len(categorical_variable) == 1, "Only one categorical variable allowed"
            st.subheader("Histogram")
            st.plotly_chart(
                StackedHistogram(color_generator=ColorGenerator(color_cache=st.session_state)).plot(
                    distribution_variables=distribution_variables,
                    categorical_variable=categorical_variable[0],
                    dataframe=filtered_df,
                    axis_config=PlotlyAxisUpdaterConfig(
                        y_max_value=max_value_y_axis if enable_max_value_y_axis else None,
                        reference_variable_name=reference_name,
                        percentage_values=percentage_values,
                        categorical_variable=categorical_variable[0],
                        distribution_variables=distribution_variables,
                    ),
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
                    axis_config=PlotlyAxisUpdaterConfig(
                        y_max_value=max_value_y_axis if enable_max_value_y_axis else None,
                        reference_variable_name=reference_name,
                        percentage_values=percentage_values,
                        categorical_variable=categorical_variable[0]
                        if categorical_variable
                        else None,
                        distribution_variables=distribution_variables,
                    ),
                )
            )
            st.divider()
        else:
            st.text("Select variables to analyze :)")
