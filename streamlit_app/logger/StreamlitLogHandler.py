import logging
from datetime import datetime
from typing import Optional

import streamlit as st
from streamlit.delta_generator import DeltaGenerator


class StreamlitLogHandler(logging.Handler):
    CONTAINER_ID = "streamlit-logger-container"

    COLOR_LEVELS = {
        "DEBUG": "violet",
        "INFO": "blue",
        "WARNING": "orange",
        "ERROR": "red",
    }

    def __init__(self, container: Optional[DeltaGenerator] = None):
        super().__init__()
        if StreamlitLogHandler.CONTAINER_ID in st.session_state:
            self._container = st.session_state[StreamlitLogHandler.CONTAINER_ID]
        else:
            if container:
                self._container = container
            else:
                with st.expander("Streamlit Logger", expanded=False):
                    self._container = st.container()
            st.session_state[StreamlitLogHandler.CONTAINER_ID] = self._container

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno == logging.DEBUG:
            self.debug(record.message)
        elif record.levelno == logging.INFO:
            self.info(record.message)
        elif record.levelno == logging.WARNING:
            self.warning(record.message)
        elif record.levelno == logging.ERROR:
            self.error(record.message)
        else:
            self._container.markdown(self.__format_message(record.message, record.levelname))

    def debug(self, message: str) -> None:
        self._container.markdown(self.__format_message(message, "DEBUG"))

    def info(self, message: str) -> None:
        self._container.markdown(self.__format_message(message, "INFO"))

    def warning(self, message: str) -> None:
        self._container.markdown(self.__format_message(message, "WARNING"))

    def error(self, message: str) -> None:
        self._container.markdown(self.__format_message(message, "ERROR"))

    def __format_message(self, message: str, level: str) -> str:
        return (
            f":{self.COLOR_LEVELS[level]}[{self.__date_format()} - **{level.upper()}**: {message}]"
        )

    def __date_format(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(format)
