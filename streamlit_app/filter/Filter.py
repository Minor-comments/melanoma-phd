from typing import Any, Dict, Protocol

import pandas as pd


class Filter(Protocol):
    def select(self) -> None:
        pass

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass

    def save_to_dict(self, dict: Dict[str, Any]) -> None:
        pass

    def load_from_dict(self, dict: Dict[str, Any]) -> None:
        pass
