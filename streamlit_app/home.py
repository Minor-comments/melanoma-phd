import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer
from streamlit_app.AppLoader import (
    AppLoader,  # isort: skip <- Force to be after workaround
    create_database_section,
    select_filters,
    select_variables,
)
from streamlit_app.latex.LaTeXArray import LaTeXArray

if __name__ == "__main__":
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
        selected_variables = select_variables(app)
        st.header("Descriptive Statistcs")
        if selected_variables:
            variables_statistics = {}
            for variable in selected_variables:
                variables_statistics[variable] = variable.descriptive_statistics(df_result)

            latex_array = LaTeXArray(variables_statistics)
            st.latex(latex_array.dumps())
        else:
            st.text("Select variables to analyze :)")
