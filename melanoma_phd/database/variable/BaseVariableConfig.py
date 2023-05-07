from dataclasses import KW_ONLY, dataclass


@dataclass
class BaseVariableConfig:
    _: KW_ONLY
    id: str
    name: str
    selectable: bool = True
