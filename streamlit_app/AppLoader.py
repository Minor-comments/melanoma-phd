from __future__ import annotations

import json
from datetime import datetime
from types import TracebackType
from typing import Dict, List, Optional, Type, Union

import streamlit as st
from PersistentSessionState import PersistentSessionState

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.filter.MultiScalarFilter import MultiScalarFilter
from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.MelanomaPhdApp import MelanomaPhdApp, create_melanoma_phd_app
from streamlit_app.filter.MultiSelectBinFilter import MultiSelectBinFilter
from streamlit_app.filter.MultiSelectFilter import MultiSelectFilter
from streamlit_app.VariableSelector import VariableSelector


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


def select_variables(
    app: AppLoader,
    variable_types: Optional[Union[Type[BaseVariable], List[Type[BaseVariable]]]] = None,
) -> List[BaseVariable]:
    uploaded_file = st.file_uploader(label="Upload a variable selection ⬆️", type=["json"])
    if uploaded_file:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        VariableSelector.select_variables_from_file(file_contents)
    selected_variables = []
    with st.expander("Variables to select"):
        selector = VariableSelector(app.database)
        variables_to_select = selector.get_variables_to_select(variable_types)
        st.checkbox(
            label="Select All variables",
            key="select_all_variables",
            on_change=lambda: selector.select_variables(variables_to_select)
            if st.session_state["select_all_variables"]
            else selector.deselect_variables(variables_to_select),
        )
        with st.form(key="variable_selection_form"):
            for variable in variables_to_select:
                st_variable_id = VariableSelector.get_variable_persistent_key(variable)
                if st.checkbox(
                    label=f"{variable.name} [{variable.id}]",
                    key=st_variable_id,
                ):
                    selected_variables.append(variable)
            if st.form_submit_button("Display statistics 📊"):
                data_to_save = VariableSelector.selected_variables_to_file(selected_variables)
            else:
                selected_variables = []
        if selected_variables:
            file_name = (
                "variable_selection_" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".json"
            )
            st.download_button(
                label="Download variable selection ⬇️ ", data=data_to_save, file_name=file_name
            )
        return selected_variables


class AppLoader:
    def __init__(self) -> None:
        self._app: Optional[MelanomaPhdApp] = None

    @property
    def database(self) -> PatientDatabase:
        if not self._app:
            raise RuntimeError(
                f"AppLoader class has to be initialized as context manager before accessing to database."
            )
        return self._app.database

    def __enter__(self) -> AppLoader:
        self._app = self.__load_app()
        self._persistent_session_state = PersistentSessionState()
        self._persistent_session_state.load(data_folder=self._app.config.data_folder)
        return self

    def __exit__(
        self,
        exception_type: BaseException,
        exception_value: BaseException,
        exception_traceback: TracebackType,
    ):
        pass

    @st.cache_resource(show_spinner="Loading main application & database...")
    def __load_app(_self) -> MelanomaPhdApp:
        return create_melanoma_phd_app()
