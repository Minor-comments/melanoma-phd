import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)  # isort: skip
from melanoma_phd.visualizer.SurvivalFunctionPlotter import SurvivalFunctionPlotter
from streamlit_app.AppLoader import (
    AppLoader,
    create_database_section,
    filter_database_section,
    select_filters_sidebar,
    select_group_by_sidebar,
)

if __name__ == "__main__":
    st.title("Melanoma Survival variables")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        filters = select_filters_sidebar(database)
        db_view = filter_database_section(database=database, filters=filters)
        filtered_df = db_view.dataframe

        selected_group_by = select_group_by_sidebar(database)
        if not selected_group_by:
            selected_group_by = None
        elif len(selected_group_by) == 1:
            selected_group_by = selected_group_by[0]

        survival_plot_config = dict(
            dataframe=filtered_df,
            group_by=selected_group_by,
            alpha=0.05,
            figsize=(10, 6),
            confident_interval=True,
            logx=False,
            at_risk_counts=True,
            show_censors=True,
        )
        st.header("Progression free survival (PFS)")
        st.pyplot(
            SurvivalFunctionPlotter(database.get_variable("PFS")).plot(**survival_plot_config)
        )
        st.header("Overall survival (OS)")
        st.pyplot(SurvivalFunctionPlotter(database.get_variable("OS")).plot(**survival_plot_config))
        st.header("TFS (TFS)")
        st.pyplot(
            SurvivalFunctionPlotter(database.get_variable("TFS")).plot(**survival_plot_config)
        )
