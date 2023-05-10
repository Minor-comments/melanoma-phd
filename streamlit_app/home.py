import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from melanoma_phd.database.filter.PatientDataFilterer import (
    PatientDataFilterer,
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.IterationVariable import IterationVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import (
    create_database_section,
    download_statistics,
    plot_figures,
    plot_statistics,
    select_filters,
    select_group_by,
    select_variables,
)

from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Melanoma PHD Decriptive Statistics")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        selected_group_by = select_group_by(app)
        st.subheader("Filtered data")
        with st.expander(f"Filtered dataframe"):
            df_result = PatientDataFilterer().filter(app.database, filters)
            st.text(f"{len(df_result.index)} patients match with selected filters")
            st.dataframe(df_result)

        st.subheader("Variable selection")
        selected_variables = select_variables(
            app,
            "Descriptive statistics",
            variable_types=[
                ScalarVariable,
                CategoricalVariable,
                BooleanVariable,
                IterationVariable,
            ],
        )
        st.header("Descriptive Statistcs")
        if selected_variables:
            variables_statistics = {}
            for variable in selected_variables:
                variables_statistics[variable] = variable.descriptive_statistics(
                    df_result, group_by=selected_group_by
                )
                st.write(f"{variable.name} by {[variable.name for variable in selected_group_by]}")
                st.dataframe(variables_statistics[variable])

            download_statistics(variables_statistics)
            plot_statistics(variables_statistics)
            plot_figures(variables_statistics)
        else:
            st.text("Select variables to analyze :)")
