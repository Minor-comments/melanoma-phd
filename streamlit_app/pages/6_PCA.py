import os
import sys

import pandas as pd
import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # isort: skip
from melanoma_phd.database.statistics.PcaProcessor import PcaProcessor
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.PcaPlotter import PcaPlotter
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database_section,
    select_filters_sidebar,
    select_several_variables_by_checkbox,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("PCA")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        filters = select_filters_sidebar(database)
        db_view = filter_database_section(database=database, filters=filters)
        filtered_df = db_view.dataframe

        st.subheader("Variable selection")
        pca_feature_variables, legend_variables = select_several_variables_by_checkbox(
            database,
            SelectVariableConfig(
                variable_selection_name="PCA feature variables",
                unique_form_title="Variables for featuring PCA to select",
                variable_types=[
                    ScalarVariable,
                ],
            ),
            SelectVariableConfig(
                variable_selection_name="Legend variable",
                unique_form_title="Varible to see in PCA legend",
                variable_types=[
                    ScalarVariable,
                    CategoricalVariable,
                ],
            ),
        )

        st.subheader("PCA")

        if pca_feature_variables and legend_variables:
            missing_values_threshold = st.number_input(
                "Missing values threshold", value=0.05, min_value=0.0, max_value=1.0
            )

            pca_processor = PcaProcessor(
                pca_feature_variables=pca_feature_variables,
                n_components=2,
                missing_values_threshold=missing_values_threshold,
            )
            pca_result = pca_processor.process(filtered_df)

            st.subheader("Raw dataframe")
            st.dataframe(
                pd.concat(
                    [variable.get_series(filtered_df) for variable in pca_feature_variables],
                    axis=1,
                )
            )
            st.info(
                f"Removing {len(pca_result.cleaned_data.rows_missing_values_over_threshold)} patients due to having more than {missing_values_threshold:.0%} missing values: {pca_result.cleaned_data.rows_missing_values_over_threshold}"
            )
            st.info(
                f"Removing {len(pca_result.cleaned_data.columns_missing_values_over_threshold)} features due to having more than {missing_values_threshold:.0%} missing values: {pca_result.cleaned_data.columns_missing_values_over_threshold}"
            )
            st.info(
                f"Removing {len(pca_result.cleaned_data.other_rows_with_missing_values)} patients due to having any missing value: {pca_result.cleaned_data.other_rows_with_missing_values}"
            )
            if pca_result.pca_df is not None:
                st.info(
                    f"Total {len(pca_result.pca_df)} patients and PCA features: {list(pca_result.pca_df.columns)}"
                )
                st.subheader("Preprocessed dataframe")
                st.dataframe(pca_result.pca_df)

                pca_plotter = PcaPlotter()
                st.plotly_chart(pca_plotter.plot_importance(pca_result))
                st.plotly_chart(
                    pca_plotter.plot_pca(
                        pca_result, df=filtered_df, legend_variables=legend_variables
                    )
                )
            else:
                st.warning("PCA Dataframe is empty")
