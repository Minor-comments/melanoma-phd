import os
import sys
from itertools import islice
from typing import Any, Tuple

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround
from melanoma_phd.database.filter.PatientDataFilterer import (
    PatientDataFilterer,
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import create_database_section, select_filters, select_variables
from streamlit_app.latex.LaTeXArray import LaTeXArray


def batched(iterable, chunk_size) -> Tuple[Any]:
    iterator = iter(iterable)
    while chunk := tuple(islice(iterator, chunk_size)):
        yield chunk


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
        selected_variables = select_variables(
            app, variable_types=[ScalarVariable, CategoricalVariable, BooleanVariable]
        )
        st.header("Descriptive Statistcs")
        if selected_variables:
            for selected_variables_chunk in batched(selected_variables, 50):
                variables_statistics = {}
                for variable in selected_variables_chunk:
                    variables_statistics[variable] = variable.descriptive_statistics(df_result)

                latex_array = LaTeXArray(variables_statistics)
                st.latex(latex_array.dumps())
        else:
            st.text("Select variables to analyze :)")
