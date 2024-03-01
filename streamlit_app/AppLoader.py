from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from itertools import islice
from types import TracebackType
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, Union

import pandas as pd
import streamlit as st
from PersistentSessionState import PersistentSessionState

from melanoma_phd.database.filter.CategoricalFilter import CategoricalFilter
from melanoma_phd.database.filter.IterationCategoricalFilter import (
    IterationCategoricalFilter,
)
from melanoma_phd.database.filter.IterationScalarFilter import IterationScalarFilter
from melanoma_phd.database.filter.NotEmptyVariableFilter import NotEmptyVariableFilter
from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.database.PatientDatabaseView import PatientDatabaseView
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.MelanomaPhdApp import MelanomaPhdApp, create_melanoma_phd_app
from streamlit_app.filter.Filter import Filter
from streamlit_app.filter.FilterSelection import FilterSelection
from streamlit_app.filter.MultiSelectFilter import MultiSelectFilter
from streamlit_app.filter.MultiSelectNotEmptyFilter import MultiSelectNotEmptyFilter
from streamlit_app.filter.RangeInputFilter import RangeInputFilter
from streamlit_app.logger.StreamlitLogHandler import StreamlitLogHandler
from streamlit_app.table.CsvTable import CsvTable
from streamlit_app.table.MarkdownTable import MarkdownTable
from streamlit_app.table.VariableTable import VariableTable
from streamlit_app.VariableSelector import VariableSelector


@dataclass
class SelectVariableConfig:
    variable_selection_name: str
    unique_form_title: str
    variable_types: Optional[Union[Type[BaseVariable], List[Type[BaseVariable]]]] = None


@st.cache_data
def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=True, sep=",", decimal=",", float_format="%.2f").encode(
        "utf-8"
    )


def reload_database(database: PatientDatabase) -> None:
    with st.spinner("Reloading database..."):
        database.reload()


def create_database_section(database: PatientDatabase) -> None:
    with st.expander(f"Database Source File"):
        st.subheader(f"{database.file_info}")
        st.button(
            label="Reload", on_click=lambda database=database: reload_database(database)
        )
        st.subheader(f"Datbase contents")
        st.dataframe(database.dataframe)


def create_filters(key_context: str, database: PatientDatabase) -> List[Filter]:
    reference_iteration_variable = database.get_variable("TIEMPO IT{N}")
    filters: List[Filter] = [
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("GRUPO TTM CORREGIDO")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("GRANDES GRUPOS")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("TIPO TTM ACTUAL")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("BOR")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("PROGRESIÓN EXTRACRANIAL")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("GRUPO NATERA")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(
                database.get_variable("Prior PD1-Based therapy (Y/N)")
            ),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(
                database.get_variable("Prior Braf inhibitor (Y/N)")
            ),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(
                database.get_variable(
                    "Line of treatment for the current treatment (advanced setting) eg 1L, 2L 3L…)"
                )
            ),
        ),
        RangeInputFilter(
            key_context=key_context,
            filter=IterationScalarFilter(
                name="At least one extraction time at X months",
                reference_variable=reference_iteration_variable,
                iteration_variables=database.get_iteration_variables_of(
                    reference_variable=reference_iteration_variable
                ),
            ),
            ranges_number=2,
        ),
        RangeInputFilter(
            key_context=key_context,
            filter=IterationScalarFilter(
                name="Extraction time at X months",
                reference_variable=reference_iteration_variable,
                iteration_variables=database.get_iteration_variables_of(
                    reference_variable=reference_iteration_variable
                ),
            ),
            ranges_number=1,
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("PFS 12m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("PFS 24m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("PFS 36m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("OS 12m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("OS 24m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("OS 36m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=CategoricalFilter(database.get_variable("OS 41m")),
        ),
        MultiSelectFilter(
            key_context=key_context,
            filter=IterationCategoricalFilter(
                name="IT PD",
                reference_variable=database.get_variable("IT{N} PD"),
                iteration_variables=database.get_iteration_variables_of(
                    reference_variable=reference_iteration_variable
                ),
            ),
        ),
        MultiSelectNotEmptyFilter(
            label="IT temporalidad",
            key_context=key_context,
            filters=[
                NotEmptyVariableFilter(variable=database.get_variable(variable_name))
                for variable_name in [
                    "IT baseline",
                    "IT 3m",
                    "IT 6m",
                    "IT 9m",
                    "IT 12m",
                    "IT 15m",
                    "IT 18m",
                    "IT 24m",
                    "IT 29mandbeyond",
                ]
            ],
        ),
    ]
    return filters


def select_filters_sidebar(database: PatientDatabase) -> List[Filter]:
    with st.sidebar.form("Patients Filter"):
        filters = create_filters(key_context="sidebar filter", database=database)
        for filter in filters:
            filter.select()
        st.form_submit_button("Filter")
        return filters


def select_population_section(
    population_name: str, database: PatientDatabase
) -> PatientDatabaseView:
    st.subheader(f"Filter {population_name}")
    uploaded_file = st.file_uploader(
        label=f"Upload a filter selection ⬆️", type=["json"], key=population_name
    )
    custom_population_name = st.text_input(
        "Filtered population name", value=population_name
    )
    filters = create_filters(key_context=population_name, database=database)
    filter_selection = FilterSelection(name=population_name, filters=filters)
    if uploaded_file:
        filter_selection.load_from_file(file_contents=uploaded_file.getvalue())
    with st.form(population_name):
        filter_selection.select()
        filtered = st.form_submit_button("Filter")
        if filtered:
            data_to_save = filter_selection.save_to_file()
            file_name = (
                f"filter_selection_{custom_population_name}"
                + datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
                + ".json"
            )
    if filtered:
        st.download_button(
            label=f"Download filter selection ⬇️",
            data=data_to_save,
            file_name=file_name,
            key=f"download_button_{population_name}",
        )
    st.subheader(f"Filtered {population_name}")
    return filter_database(
        unique_form_title=f"{population_name} variables to display",
        database=database,
        filters=filters,
        population_name=custom_population_name,
    )


def select_group_by_sidebar(database: PatientDatabase) -> List[BaseVariable]:
    with st.sidebar.form("Group by"):
        selected_group_by = simple_select_variables_by_checkbox(
            database,
            SelectVariableConfig(
                variable_selection_name="Categorical Group By",
                unique_form_title="Categorical Group By variables",
                variable_types=CategoricalVariable,
            ),
        )
        st.form_submit_button("Group By")
        return selected_group_by


def filter_database(
    unique_form_title: str,
    database: PatientDatabase,
    filters: List[Filter],
    population_name: str,
) -> PatientDatabaseView:
    db_view = database.filter(filters=filters, name=population_name)
    df_result = db_view.dataframe
    st.text(f"{len(df_result.index)} patients match with selected filters")
    selected_variables = select_variables_by_multiselect(
        database=database,
        select_variable_config=SelectVariableConfig(
            variable_selection_name=f"{unique_form_title}_filter_database_variable_selection",
            unique_form_title=unique_form_title,
        ),
    )
    df_result_to_display = df_result
    if selected_variables:
        df_result_to_display = df_result[
            [selected_variable.id for selected_variable in selected_variables]
        ]
    st.dataframe(df_result_to_display)
    file_name = (
        "filtered_dataframe_" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".csv"
    )
    csv = dataframe_to_csv(df_result_to_display)
    st.download_button(
        label=f"Download filtered dataframe ⬇️ ",
        data=csv,
        mime="text/csv",
        file_name=file_name,
        key=f"download_button_{unique_form_title}_filter_database",
    )
    return db_view


def filter_database_section(
    database: PatientDatabase, filters: List[Filter]
) -> PatientDatabaseView:
    st.subheader("Filtered data")
    with st.expander(f"Filtered dataframe"):
        return filter_database(
            unique_form_title="Variables to display",
            database=database,
            filters=filters,
            population_name="",
        )


def select_variables_by_checkbox(
    database: PatientDatabase, select_variable_config: SelectVariableConfig
) -> List[BaseVariable]:
    variable_selection_name = select_variable_config.variable_selection_name
    variable_types = select_variable_config.variable_types

    uploaded_file = st.file_uploader(
        label=f"Upload a '{variable_selection_name}' variable selection ⬆️",
        type=["json"],
    )
    if uploaded_file:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        VariableSelector.select_variables_from_file(
            variable_selection_name, file_contents
        )
    selected_variables: List[BaseVariable] = []
    with st.expander(select_variable_config.unique_form_title):
        selector = VariableSelector(database)
        variables_to_select = selector.get_variables_to_select(variable_types)
        st.checkbox(
            label=f"Select All",
            key=f"select_variables_{variable_selection_name}",
            on_change=lambda: (
                selector.select_variables(variable_selection_name, variables_to_select)
                if st.session_state[f"select_variables_{variable_selection_name}"]
                else selector.deselect_variables(
                    variable_selection_name, variables_to_select
                )
            ),
        )
        with st.form(key=f"variable_selection_form_{variable_selection_name}"):
            selected_variables = []
            for variable in variables_to_select:
                st_variable_id = VariableSelector.get_variable_persistent_key(
                    variable_selection_name, variable
                )
                if st.checkbox(
                    label=f"{variable.name} [{variable.id}]",
                    key=st_variable_id,
                ):
                    selected_variables.append(variable)
            if st.form_submit_button("Display statistics 📊"):
                data_to_save = VariableSelector.selected_variables_to_file(
                    variable_selection_name, selected_variables
                )
            else:
                selected_variables = []
        if selected_variables:
            file_name = (
                "variable_selection_"
                + datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
                + ".json"
            )
            st.download_button(
                label=f"Download '{variable_selection_name}' variable selection ⬇️ ",
                data=data_to_save,
                file_name=file_name,
            )
        return selected_variables


def select_several_variables_by_checkbox(
    database: PatientDatabase, *select_variable_config: SelectVariableConfig
) -> Tuple[List[BaseVariable], ...]:
    with st.form(
        key=f"variable_selection_form_{'-'.join([c.variable_selection_name for c in select_variable_config])}"
    ):
        selected_variables = []
        for config in select_variable_config:
            selected_variables.append(
                simple_select_variables_by_checkbox(database, config)
            )
        if not st.form_submit_button("Display statistics 📊"):
            selected_variables = [[] for _ in select_variable_config]
    return tuple(selected_variables)


def simple_select_variables_by_checkbox(
    database: PatientDatabase, select_variable_config: SelectVariableConfig
) -> List[BaseVariable]:
    with st.expander(select_variable_config.unique_form_title):
        selector = VariableSelector(database)
        variables_to_select = selector.get_variables_to_select(
            select_variable_config.variable_types
        )
        selected_variables = []
        for variable in variables_to_select:
            st_variable_id = VariableSelector.get_variable_persistent_key(
                select_variable_config.variable_selection_name, variable
            )
            if st.checkbox(
                label=f"{variable.name} [{variable.id}]",
                key=st_variable_id,
            ):
                selected_variables.append(variable)
    return selected_variables


def select_one_variable(
    database: PatientDatabase, select_variable_config: SelectVariableConfig
) -> BaseVariable:
    selected_variable = None
    with st.form(select_variable_config.unique_form_title):
        selector = VariableSelector(database)
        variables = selector.get_variables_to_select(
            select_variable_config.variable_types
        )
        variable_ids = [variable.id for variable in variables]
        selected_variables_id = st.selectbox(
            label="Select variable to display",
            options=variable_ids,
            key=select_variable_config.variable_selection_name,
        )
        if st.form_submit_button("Display variable"):
            selected_variable = database.get_variable(selected_variables_id)
    return selected_variable


def select_variables_by_multiselect(
    database: PatientDatabase, select_variable_config: SelectVariableConfig
) -> List[BaseVariable]:
    selected_variables = []
    variables: List[BaseVariable] = database.get_variables_by_type(
        select_variable_config.variable_types
    )
    variables.remove(database.index_variable)
    uploaded_file = st.file_uploader(
        label=f"Upload a filtered dataframe variable selection ⬆️",
        type=["json"],
        key="file_uploader_" + select_variable_config.variable_selection_name,
    )
    default_selected_variables = []
    if uploaded_file:
        file_contents = uploaded_file.getvalue()
        default_selected_variables = VariableSelector.get_selected_variables_from_file(
            context_uid=select_variable_config.variable_selection_name,
            file_contents=file_contents,
            variables=variables,
        )
    with st.form(select_variable_config.unique_form_title):
        variable_ids = [variable.id for variable in variables]
        default_variable_ids = [variable.id for variable in default_selected_variables]
        selected_variables_ids = st.multiselect(
            label="Select variables to display",
            options=variable_ids,
            default=default_variable_ids,
            key=select_variable_config.variable_selection_name,
        )
        if st.form_submit_button("Display variables"):
            selected_variables = database.get_variables(selected_variables_ids)
            data_to_save = VariableSelector.selected_variables_to_file(
                context_uid=select_variable_config.variable_selection_name,
                variables=selected_variables,
            )

        file_name = (
            select_variable_config.variable_selection_name
            + datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
            + ".json"
        )
    if selected_variables:
        st.download_button(
            label=f"Download '{select_variable_config.variable_selection_name}' variable selection ⬇️ ",
            data=data_to_save,
            file_name=file_name,
        )

    return selected_variables


def batched_dict(iterable: Dict[Any, Any], chunk_size: int) -> Iterator[Any]:
    iterator = iter(iterable)
    for i in range(0, len(iterable), chunk_size):
        yield {key: iterable[key] for key in islice(iterator, chunk_size)}


def download_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    table = VariableTable(variables_statistics)
    csv_creator = CsvTable(table)
    csv_contents = csv_creator.dumps()
    file_name = (
        "descriptive_statistics" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".csv"
    )
    st.download_button(
        label="Download as CSV ⬇️ ", data=csv_contents, file_name=file_name
    )


def plot_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    MAX_VARIABLES_TABLE = 100
    for variables_statistics_chunk in batched_dict(
        variables_statistics, MAX_VARIABLES_TABLE
    ):
        table = VariableTable(variables_statistics_chunk)
        markdown_table = MarkdownTable(table)
        st.markdown(markdown_table.dumps(), unsafe_allow_html=True)
        if len(variables_statistics) > MAX_VARIABLES_TABLE:
            st.markdown(
                f"📃 :orange[Only displaying the first {MAX_VARIABLES_TABLE} variables for performance issues.]"
            )
        return


class AppLoader:
    def __init__(self, log_trace: bool = False) -> None:
        self._app: Optional[MelanomaPhdApp] = None
        self._log_trace: bool = log_trace

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
        custom_handlers = [StreamlitLogHandler()] if _self._log_trace else []
        return create_melanoma_phd_app(
            log_level=logging.INFO, custom_handlers=custom_handlers
        )
