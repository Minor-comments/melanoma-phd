from typing import Dict, Union

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable


class BooleanVariable(CategoricalVariable):
    def __init__(
        self, id: str, name: str, category_name_values: Dict[Union[int, str], str] = None
    ) -> None:
        category_name_values = category_name_values if category_name_values else {0: "No", 1: "Yes"}
        super().__init__(id=id, name=name, category_name_values=category_name_values)
