from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class BaseVariable:
    name: str


class CategoricalVariable(BaseVariable):
    def __init__(self, name: str, category_names: Dict[Union[int, float, str], str]) -> None:
        super().__init__(name)
        self._category_names = category_names

    @property
    def category_name(self) -> str:
        return self._category_names

    def get_category_name(self, value: Union[int, float, str]) -> str:
        return self._category_names.get(value, str(value))


class ScaleVarible(BaseVariable):
    def __init__(self, name: str) -> None:
        super().__init__(name)
