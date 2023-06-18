import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.visualizer.SurvivalFunctionPlotter import SurvivalFunctionPlotter
from streamlit_app.AppLoader import (
    create_database_section,
    filter_database,
    select_filters,
    select_group_by,
)

from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround

if __name__ == "__main__":
    st.title("Melanoma Survival variables")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        df_result = filter_database(app=app, filters=filters)

        selected_group_by = select_group_by(app)
        if not selected_group_by:
            selected_group_by = None
        elif len(selected_group_by) == 1:
            selected_group_by = selected_group_by[0]

        survival_plot_config = dict(
            dataframe=df_result,
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
            SurvivalFunctionPlotter(app.database.get_variable("PFS")).plot(**survival_plot_config)
        )
        st.header("Overall survival (OS)")
        st.pyplot(
            SurvivalFunctionPlotter(app.database.get_variable("OS")).plot(**survival_plot_config)
        )
        st.header("TFS (TFS)")
        st.pyplot(
            SurvivalFunctionPlotter(app.database.get_variable("TFS")).plot(**survival_plot_config)
        )
