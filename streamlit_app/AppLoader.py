from __future__ import annotations

from types import TracebackType

import streamlit as st

from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.MelanomaPhdApp import MelanomaPhdApp, create_melanoma_phd_app


class AppLoader:
    def __init__(self) -> None:
        self._app = None

    @property
    def database(self) -> PatientDatabase:
        if not self._app:
            raise RuntimeError(
                f"AppLoader class has to be initialized as context manager before accessing to database."
            )
        return self._app.database

    def __enter__(self) -> AppLoader:
        self._app = self.__load_app()
        return self

    def __exit__(
        self,
        exception_type: BaseException,
        exception_value: BaseException,
        exception_traceback: TracebackType,
    ):
        pass

    @st.experimental_singleton(show_spinner="Loading the main app...")
    def __load_app(_self) -> MelanomaPhdApp:
        return create_melanoma_phd_app()
