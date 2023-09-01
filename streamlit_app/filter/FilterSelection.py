import json
from typing import Any, Dict, List

import pandas as pd

from streamlit_app.filter.Filter import Filter


class FilterSelection:
    def __init__(self, name: str, filters: List[Filter]) -> None:
        self._name = name
        self._filters = filters

    def select(self) -> None:
        for filter in self._filters:
            filter.select()

    def save_to_file(self) -> str:
        dict: Dict[str, Any] = {}
        for filter in self._filters:
            filter.save_to_dict(dict)
        return bytes(json.dumps(dict), "utf-8")

    def load_from_file(self, file_contents: bytes) -> None:
        dict: Dict[str, Any] = json.loads(file_contents.decode("utf-8"))
        for filter in self._filters:
            filter.load_from_dict(dict)
