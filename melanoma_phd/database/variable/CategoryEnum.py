from enum import Enum

from typing_extensions import Self


class CategoryEnum(Enum):
    def __new__(cls, value, description) -> Self:
        entry = object.__new__(cls)
        entry._value_ = value
        entry.description = description
        return entry

    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}: ({self.value!r}, {self.description!r})>"

    @property
    def option_name(self) -> str:
        return f"{self.name}({self.value})"
