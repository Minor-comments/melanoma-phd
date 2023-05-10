import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.visualizer.SurvivalFunctionPlotter import SurvivalFunctionPlotter
from streamlit_app.AppLoader import (create_database_section, select_filters, select_group_by,
                                     select_variables)

from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround

if __name__ == "__main__":
    st.title("Melanoma Survival variables")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        st.subheader("Filtered data")
        with st.expander(f"Filtered dataframe"):
            df_result = PatientDataFilterer().filter(app.database, filters)
            st.text(f"{len(df_result.index)} patients match with selected filters")
            st.dataframe(df_result)

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
