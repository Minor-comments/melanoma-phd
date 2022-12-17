import os
import sys
from typing import List

import streamlit as st
from PersistentSessionState import PersistentSessionState

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.filter.MultiScalarFilter import MultiScalarFilter
from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from streamlit_app.filter.MultiSelectBinFilter import MultiSelectBinFilter
from streamlit_app.filter.MultiSelectFilter import MultiSelectFilter


def reload_database(app: AppLoader) -> None:
    with st.spinner("Reloading database..."):
        app.database.reload()


def create_database_section(app: AppLoader) -> None:
    with st.expander(f"Database Source File"):
        st.subheader(f"{app.database.file_info}")
        st.button(label="Reload", on_click=lambda app=app: reload_database(app))
        st.subheader(f"Datbase contents")
        st.dataframe(app.database.dataframe)


def select_filters(app: AppLoader) -> List[MultiSelectFilter]:
    with st.sidebar.form("Patients Filter"):
        # TODO: Create filter factory from .yaml file
        filters = [
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("GRUPO TTM CORREGIDO"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("TIPO TTM ACTUAL"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("BOR"))),
            MultiSelectBinFilter(
                filter=MultiScalarFilter(
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
                ),
                bins={
                    "0-2 months": "[0, 2]",
                    "3-5 months": "[3, 5]",
                    "6-8 months": "[6, 8]",
                    "9-11 months": "[9, 11]",
                    "12-14 months": "[12, 14]",
                    "15-17 months": "[15, 17]",
                    "18-20 months": "[18, 20]",
                    "21-24 months": "[21, 24]",
                },
            ),
        ]
        for filter in filters:
            filter.select()
        st.form_submit_button("Filter")
        return filters


def select_variables(app: AppLoader) -> List[BaseVariable]:
    selected_variables = []
    with st.expander("Variables to select"):
        with st.form(key="variable_selection_form"):
            for database_sheet in app.database.sheets:
                st.subheader(f"{database_sheet.name} variables")
                for variable in database_sheet.variables:
                    st_variable_id = PersistentSessionState.persist_key(
                        f"{database_sheet.name}.{variable.id}"
                    )
                    if st.checkbox(
                        f"{variable.name} [{variable.id}]",
                        key=st_variable_id,
                    ):
                        selected_variables.append(variable)
            if st.form_submit_button("Display statistics"):
                return selected_variables
            else:
                return []


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
            for variable in selected_variables:
                st.text(variable.name)
                st.dataframe(variable.descriptive_statistics(df_result))
        else:
            st.text("Select variables to analyze :)")
