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
    AppLoader,  # isort: skip <- Force to be after workaround
    create_database_section,
    download_statistics,
    plot_figures,
    plot_statistics,
    select_filters,
    select_variables,
)

if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Melanoma PHD Statistics")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        st.subheader("Filtered data")
        with st.expander(f"Filtered dataframe"):
            df_result = PatientDataFilterer().filter(app.database, filters)
            st.text(f"{len(df_result.index)} patients match with selected filters")
            st.dataframe(df_result)

        st.subheader("Variable selection")
        selected_variables = select_variables(
            app,
            variable_types=[
                ScalarVariable,
                CategoricalVariable,
                BooleanVariable,
                IterationVariable,
            ],
        )

        st.subheader("Categorical Group By selection")
        selected_group_by_variables = select_variables(
            app,
            variable_types=CategoricalVariable,
            displayed_title="Categorical Group By variables",
        )
        st.header("Descriptive Statistcs")
        if selected_variables and selected_group_by_variables:
            variables_statistics = {}
            for variable in selected_variables:
                variables_statistics[variable] = variable.descriptive_statistics(
                    df_result, group_by_id=selected_group_by_variables
                )

            download_statistics(variables_statistics)
            plot_statistics(variables_statistics)
            plot_figures(variables_statistics)
        else:
            st.text("Select variables to analyze :)")
