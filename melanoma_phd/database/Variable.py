from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Union


class MeasurementLevel(Enum):
    # Data with a limited number of distinct values or categories
    CATEGORICAL = auto()
    # Data measured on an interval or ratio scale, where the data values indicate both the order of values and the distance between values.
    SCALE = auto()


@dataclass
class BaseVariable:
    name: str


class CategoricalVariable(BaseVariable):
    def __init__(self, name: str, category_names: Dict[Union[int, str], str]) -> None:
        super().__init__(name)
        self._category_names = category_names

    @property
    def category_name(self) -> str:
        return self._category_names

    def get_category_name(self, value: Union[str, int]) -> str:
        return self._category_names.get(int(value), str(value))


class ScaleVarible(BaseVariable):
    def __init__(self, name: str) -> None:
        super().__init__(name)
