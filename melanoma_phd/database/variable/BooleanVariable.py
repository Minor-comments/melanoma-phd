from typing import Dict, Optional, Union

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable


class BooleanVariable(CategoricalVariable):
    def __init__(
        self,
        id: str,
        name: str,
        categories: Optional[Dict[Union[int, float, str], str]] = None,
    ) -> None:
        categories = categories if categories else lambda x: "Yes" if x else "No"
        super().__init__(id=id, name=name, categories=categories)
