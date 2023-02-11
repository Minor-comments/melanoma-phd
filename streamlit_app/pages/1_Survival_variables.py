import os
import sys

import streamlit as st
from melanoma_phd.database.variable.CategoricalVariable import (
    CategoricalVariable,
)
from melanoma_phd.visualizer.SurvivalFunctionPlotter import (
    SurvivalFunctionPlotter,
)
from streamlit_app.AppLoader import (
    create_database_section,
    select_filters,
    select_variables,
)

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import (
    AppLoader,
)  # isort: skip <- Force to be after workaround

from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer


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

        st.subheader("Variable selection")
        selected_variables = select_variables(app, variable_types=CategoricalVariable)
        if not selected_variables:
            selected_variables = None
        elif len(selected_variables) == 1:
            selected_variables = selected_variables[0]

        survival_plot_config = dict(
            dataframe=df_result,
            group_by=selected_variables,
            alpha=0.05,
            figsize=(10, 6),
            confident_interval=True,
            logx=False,
            at_risk_counts=True,
            show_censors=True,
        )
        st.header("Progression free survival (PFS)")
        st.pyplot(
            SurvivalFunctionPlotter(app.database.get_variable("PFS")).plot(
                **survival_plot_config
            )
        )
        st.header("Overall survival (OS)")
        st.pyplot(
            SurvivalFunctionPlotter(app.database.get_variable("OS")).plot(
                **survival_plot_config
            )
        )
        st.header("TFS (TFS)")
        st.pyplot(
            SurvivalFunctionPlotter(app.database.get_variable("TFS")).plot(
                **survival_plot_config
            )
        )
