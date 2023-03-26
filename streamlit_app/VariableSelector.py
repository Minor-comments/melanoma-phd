import json
from typing import List, Optional, Type, Union

import streamlit as st

from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from streamlit_app.PersistentSessionState import PersistentSessionState


class VariableSelector:
    def __init__(self, database: PatientDatabase) -> None:
        self._database = database

    def get_variables_to_select(
        self, variable_types: Optional[Union[Type[BaseVariable], List[Type[BaseVariable]]]] = None
    ) -> List[BaseVariable]:
        if variable_types and isinstance(variable_types, Type):
            variable_types = [variable_types]
        variables_to_select = []
        for database_sheet in self._database.sheets:
            for variable in database_sheet.variables:
                if variable_types and not any(
                    isinstance(variable, variable_type) for variable_type in variable_types
                ) or not variable.selectable:
                    continue
                variables_to_select.append(variable)
        return variables_to_select

    def select_variables(self, variables: List[BaseVariable]) -> None:
        for variable in variables:
            st.session_state[self.get_variable_persistent_key(variable)] = True

    def deselect_variables(self, variables: List[BaseVariable]) -> None:
        for variable in variables:
            st.session_state[self.get_variable_persistent_key(variable)] = False

    @staticmethod
    def get_variable_persistent_key(variable: BaseVariable) -> str:
        return VariableSelector.get_variable_persistent_key_from_uid(
            variable_uid=variable.unique_id
        )

    @staticmethod
    def get_variable_persistent_key_from_uid(variable_uid: str) -> str:
        return PersistentSessionState.persist_key(key=variable_uid)

    @staticmethod
    def selected_variables_to_file(variables: List[BaseVariable]) -> bytes:
        return json.dumps(
            {"selected_variables_uids": [variable.unique_id for variable in variables]}
        ).encode("utf-8")

    @staticmethod
    def select_variables_from_file(file_contents: str) -> None:
        file_json = json.loads(file_contents)
        for variable_uid in file_json["selected_variables_uids"]:
            st.session_state[
                VariableSelector.get_variable_persistent_key_from_uid(variable_uid)
            ] = True
