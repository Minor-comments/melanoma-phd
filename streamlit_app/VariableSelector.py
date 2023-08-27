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
        for variable in self._database.variables:
            if all(
                [
                    variable.selectable,
                    any(isinstance(variable, variable_type) for variable_type in variable_types)
                    if variable_types
                    else True,
                ]
            ):
                variables_to_select.append(variable)
        return variables_to_select

    def select_variables(self, context_uid: str, variables: List[BaseVariable]) -> None:
        for variable in variables:
            st.session_state[self.get_variable_persistent_key(context_uid, variable)] = True

    def deselect_variables(self, context_uid: str, variables: List[BaseVariable]) -> None:
        for variable in variables:
            st.session_state[self.get_variable_persistent_key(context_uid, variable)] = False

    @staticmethod
    def get_variable_persistent_key(context_uid: str, variable: BaseVariable) -> str:
        return VariableSelector.get_variable_persistent_key_from_uid(
            context_uid=context_uid, variable_uid=variable.unique_id
        )

    @staticmethod
    def get_variable_persistent_key_from_uid(context_uid: str, variable_uid: str) -> str:
        return f"{context_uid}_{PersistentSessionState.persist_key(key=variable_uid)}"

    @staticmethod
    def selected_variables_to_file(context_uid: str, variables: List[BaseVariable]) -> bytes:
        return json.dumps(
            {
                f"{context_uid}_selected_variables_uids": [
                    variable.unique_id for variable in variables
                ]
            }
        ).encode("utf-8")

    @staticmethod
    def get_selected_variables_from_file(
        context_uid: str, file_contents: bytes, variables: List[BaseVariable]
    ) -> List[BaseVariable]:
        loaded_variables = json.loads(file_contents.decode("utf-8"))[
            f"{context_uid}_selected_variables_uids"
        ]
        return [variable for variable in variables if variable.unique_id in loaded_variables]

    @staticmethod
    def select_variables_from_file(context_uid: str, file_contents: str) -> None:
        file_json = json.loads(file_contents)
        for variable_uid in file_json[f"{context_uid}_selected_variables_uids"]:
            st.session_state[
                VariableSelector.get_variable_persistent_key_from_uid(context_uid, variable_uid)
            ] = True
