import os
import sys
from typing import List

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.filter.MultiScalarFilter import MultiScalarFilter
from melanoma_phd.database.filter.PatientDataFilterer import \
    PatientDataFilterer
from melanoma_phd.database.filter.ScalarFilter import ScalarFilter
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from streamlit_app.filter.MultiSelectFilter import MultiSelectFilter
from streamlit_app.filter.RangeSliderFilter import RangeSliderFilter


def reload_database(app: AppLoader) -> None:
    with st.spinner("Reloading database..."):
        app.database.reload()


def create_database_section(app: AppLoader) -> None:
    with st.expander(f"Database Source File"):
        st.subheader(f"{app.database.file_info}")
        st.button(label="Reload", on_click=lambda app=app: reload_database(app))
        st.subheader(f"Datbase contents")
        st.dataframe(app.database.dataframe)


def select_variables(app: AppLoader) -> List[BaseVariable]:
    selected_variables = []
    st.subheader("Variables to select")
    for database_sheet in app.database.sheets:
        with st.expander(f"{database_sheet.name} variables"):
            for variable in database_sheet.variables:
                st_variable_id = f"{database_sheet.name}.{variable.id}"
                if st.checkbox(f"{variable.name} [{variable.id}]", key=st_variable_id):
                    selected_variables.append(variable)
    if not selected_variables:
        selected_variables = app.database.variables[:25]
    return selected_variables


def select_filters(app: AppLoader) -> List[MultiSelectFilter]:
    with st.sidebar.form("Patients Filter"):
        filters = [
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("GRUPO TTM CORREGIDO"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("TIPO TTM ACTUAL"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("BOR"))),
            RangeSliderFilter(
                MultiScalarFilter(
                    name="Extraction time",
                    variables=[
                        app.database.get_variable("TIEMPO IT1"),
                        app.database.get_variable("TIEMPO IT2"),
                        app.database.get_variable("TIEMPO IT3"),
                        app.database.get_variable("TIEMPO IT4"),
                        app.database.get_variable("TIEMPO IT5"),
                        app.database.get_variable("TIEMPO IT6"),
                        app.database.get_variable("TIEMPO IT7"),
                        app.database.get_variable("TIEMPO IT8"),
                        app.database.get_variable("TIEMPO IT9"),
                        app.database.get_variable("TIEMPO IT10"),
                    ],
                )
            ),
            RangeSliderFilter(ScalarFilter(app.database.get_variable("PFS DURATION"))),
            RangeSliderFilter(ScalarFilter(app.database.get_variable("OS DURATION"))),
        ]
        for filter in filters:
            filter.select()
        st.form_submit_button("Filter")
        return filters


if __name__ == "__main__":
    st.title("Melanoma PHD Statistics")
    with AppLoader() as app:
        create_database_section(app)
        selected_variables = select_variables(app)

        filters = select_filters(app)
        st.subheader("Filtered data")
        with st.expander(f"Filtered dataframe"):
            df_result = PatientDataFilterer().filter(app.database, filters)
            st.dataframe(df_result)

        st.header("Descriptive Statistcs")
        if selected_variables:
            for variable in selected_variables:
                st.text(variable.name)
                st.dataframe(variable.descriptive_statistics(df_result))
        else:
            st.text("Select variables to analyze :)")
