from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Union

import pandas as pd


@dataclass
class BaseVariable(ABC):
    id: str
    name: str

    @abstractmethod
    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        pass


class CategoricalVariable(BaseVariable):
    def __init__(
        self, id: str, name: str, category_name_values: Dict[Union[int, str], str]
    ) -> None:
        super().__init__(id=id, name=name)
        self._category_name_values = category_name_values

    @property
    def category_names(self) -> List[str]:
        return self._category_name_values.values()

    @property
    def category_values(self) -> List[str]:
        return self._category_name_values.keys()

    def get_category_name(self, value: Union[int, float, str]) -> str:
        return self._category_name_values.get(value, str(value))

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe[self.id].map(self._category_name_values)
        counts = dataframe.value_counts()
        percent = dataframe.value_counts(normalize=True)
        percent100 = percent.mul(100).round(1).astype(str) + "%"
        return pd.DataFrame({"counts": counts, "per": percent, "per100": percent100})


class ScaleVarible(BaseVariable):
    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id, name=name)


class BooleanVariable(CategoricalVariable):
    def __init__(
        self, id: str, name: str, category_name_values: Dict[Union[int, str], str] = None
    ) -> None:
        category_name_values = category_name_values if category_name_values else {0: "No", 1: "Yes"}
        super().__init__(id=id, name=name, category_name_values=category_name_values)
