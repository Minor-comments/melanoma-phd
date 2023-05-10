from __future__ import annotations

from datetime import datetime
from itertools import islice
from types import TracebackType
from typing import Any, Dict, Iterator, List, Optional, Type, Union

import pandas as pd
import streamlit as st
from PersistentSessionState import PersistentSessionState

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.filter.IterationFilter import IterationFilter
from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.MelanomaPhdApp import MelanomaPhdApp, create_melanoma_phd_app
from melanoma_phd.visualizer.PiePlotter import PiePlotter
from streamlit_app.filter.Filter import Filter
from streamlit_app.filter.MultiSelectFilter import MultiSelectFilter
from streamlit_app.filter.RangeSliderFilter import RangeSliderFilter
from streamlit_app.table.CsvTable import CsvTable
from streamlit_app.table.MarkdownTable import MarkdownTable
from streamlit_app.table.VariableTable import VariableTable
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


def select_filters(app: AppLoader) -> List[Filter]:
    with st.sidebar.form("Patients Filter"):
        # TODO: Create filter factory from .yaml file
        reference_iteration_variable = app.database.get_variable("TIEMPO IT{N}")
        filters: List[Filter] = [
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("GRUPO TTM CORREGIDO"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("TIPO TTM ACTUAL"))),
            MultiSelectFilter(CategoricalFilter(app.database.get_variable("BOR"))),
            RangeSliderFilter(
                filter=IterationFilter(
                    name="Extraction time (time in months)",
                    reference_variable=reference_iteration_variable,
                    iteration_variables=app.database.get_iteration_variables_of(
                        reference_variable=reference_iteration_variable
                    ),
                ),
                min_value=0,
                max_value=None,
            ),
        ]
        for filter in filters:
            filter.select()
        st.form_submit_button("Filter")
        return filters


def select_group_by(app: AppLoader) -> List[BaseVariable]:
    with st.sidebar.form("Group by"):
        selected_group_by = simple_select_variables(
            app,
            "Categorical Group By",
            variable_types=CategoricalVariable,
            displayed_title="Categorical Group By variables",
        )
        st.form_submit_button("Group By")
        return selected_group_by


def select_variables(
    app: AppLoader,
    variable_selection_name: str,
    variable_types: Optional[Union[Type[BaseVariable], List[Type[BaseVariable]]]] = None,
    displayed_title: Optional[str] = None,
) -> List[BaseVariable]:
    uploaded_file = st.file_uploader(
        label=f"Upload a '{variable_selection_name}' variable selection ⬆️", type=["json"]
    )
    if uploaded_file:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        VariableSelector.select_variables_from_file(file_contents)
    selected_variables = []
    displayed_title = displayed_title or "Variables to select"
    with st.expander(displayed_title):
        selector = VariableSelector(app.database)
        variables_to_select = selector.get_variables_to_select(variable_types)
        st.checkbox(
            label=f"Select '{variable_selection_name}' variables",
            key=f"select_variables_{variable_selection_name}",
            on_change=lambda: selector.select_variables(variables_to_select)
            if st.session_state[f"select_variables_{variable_selection_name}"]
            else selector.deselect_variables(variables_to_select),
        )
        with st.form(key=f"variable_selection_form_{variable_selection_name}"):
            selected_variables = _generate_selected_variable_checkboxs(
                variables_to_select, variable_selection_name
            )
            if st.form_submit_button("Display statistics 📊"):
                data_to_save = VariableSelector.selected_variables_to_file(selected_variables)
            else:
                selected_variables = []
        if selected_variables:
            file_name = (
                "variable_selection_" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".json"
            )
            st.download_button(
                label=f"Download '{variable_selection_name}' variable selection ⬇️ ",
                data=data_to_save,
                file_name=file_name,
            )
        return selected_variables


def simple_select_variables(
    app: AppLoader,
    variable_selection_name: str,
    variable_types: Optional[Union[Type[BaseVariable], List[Type[BaseVariable]]]] = None,
    displayed_title: Optional[str] = None,
) -> List[BaseVariable]:
    displayed_title = displayed_title or "Variables to select"
    with st.expander(displayed_title):
        selector = VariableSelector(app.database)
        variables_to_select = selector.get_variables_to_select(variable_types)
        selected_variables = _generate_selected_variable_checkboxs(
            variables_to_select, variable_selection_name
        )

    return selected_variables


def _generate_selected_variable_checkboxs(
    variables: List[BaseVariable], variable_selection_name: str
) -> List[BaseVariable]:
    selected_variables = []
    for variable in variables:
        st_variable_id = (
            f"{variable_selection_name}_{VariableSelector.get_variable_persistent_key(variable)}"
        )
        if st.checkbox(
            label=f"{variable.name} [{variable.id}]",
            key=st_variable_id,
        ):
            selected_variables.append(variable)
    return selected_variables


def batched_dict(iterable: Dict[Any, Any], chunk_size: int) -> Iterator[Any]:
    iterator = iter(iterable)
    for i in range(0, len(iterable), chunk_size):
        yield {key: iterable[key] for key in islice(iterator, chunk_size)}


def download_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    table = VariableTable(variables_statistics)
    csv_creator = CsvTable(table)
    csv_contents = csv_creator.dumps()
    file_name = "descriptive_statistics" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".csv"
    st.download_button(label="Download as CSV ⬇️ ", data=csv_contents, file_name=file_name)


def plot_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    MAX_VARIABLES_TABLE = 100
    for variables_statistics_chunk in batched_dict(variables_statistics, MAX_VARIABLES_TABLE):
        table = VariableTable(variables_statistics_chunk)
        markdown_table = MarkdownTable(table)
        st.markdown(markdown_table.dumps(), unsafe_allow_html=True)
        if len(variables_statistics) > MAX_VARIABLES_TABLE:
            st.markdown(
                f"📃 :orange[Only displaying the first {MAX_VARIABLES_TABLE} variables for performance issues.]"
            )
        return


def plot_figures(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    variable_names_to_plot = ["T(CD3+)({N})", "LB(CD19+)({N})", "NK(CD16/56+)({N})"]
    variables_to_plot = dict(
        (variable, statistics)
        for variable, statistics in variables_statistics.items()
        if variable.id in variable_names_to_plot
    )
    st.pyplot(PiePlotter().plot(variable_statistics=variables_to_plot))


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
