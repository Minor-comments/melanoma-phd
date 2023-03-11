import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

import streamlit as st


class PersistentSessionState:
    _PERSISTENT_STATE_KEY_PREFIX = f"PERSISTENT_"

    def __init__(self):
        pass

    @classmethod
    def persist_key(cls, key: str) -> str:
        return cls._PERSISTENT_STATE_KEY_PREFIX + key

    def load(self, data_folder: str) -> None:
        current_persistent_dict = self.__get_current_persistent_dict()
        if data_folder:
            loaded_persistent_dict = self.__get_disk_persistent_state(data_folder=data_folder)
            loaded_persistent_dict.update(current_persistent_dict)
            current_persistent_dict = loaded_persistent_dict
            self.__save_disk_persistent_state(
                current_persistent_dict=current_persistent_dict, data_folder=data_folder
            )
        st.session_state.update(current_persistent_dict)

    def __get_current_persistent_dict(self) -> Dict[str, Any]:
        return {
            key: value
            for key, value in st.session_state.items()
            if key.startswith(self._PERSISTENT_STATE_KEY_PREFIX)
        }

    def __get_file_path(self, data_folder: str) -> Path:
        return (Path(data_folder) / "streamlit" / "persistent_state.json").resolve()

    def __get_disk_persistent_state(self, data_folder: str) -> Dict[str, Any]:
        persisten_state_file = self.__get_file_path(data_folder)
        if os.path.exists(persisten_state_file):
            try:
                with open(persisten_state_file, "r") as f:
                    loaded_persistent_dict = json.load(f)
            except json.JSONDecodeError as e:
                loaded_persistent_dict = {}
                logging.warning(
                    f"Failed to load persistent state from {persisten_state_file}. Error: {e}"
                )
            return loaded_persistent_dict
        return {}

    def __save_disk_persistent_state(
        self, current_persistent_dict: Dict[str, Any], data_folder: str
    ) -> None:
        persisten_state_file = self.__get_file_path(data_folder)
        try:
            os.makedirs(os.path.dirname(persisten_state_file), exist_ok=True)
            with open(persisten_state_file, "w") as f:
                json.dump(current_persistent_dict, f)
        except TypeError as e:
            logging.warning(
                f"Failed to save persistent state to {persisten_state_file}. Error: {e}"
            )
