from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from melanoma_phd.database.variable.BaseVariableConfig import BaseVariableConfig
from melanoma_phd.database.variable.Variable import Variable


@dataclass
class BaseDynamicVariableConfig(BaseVariableConfig):
    required_ids: Optional[List[str]] = None
    required_variables: Optional[List[Variable]] = None


class VariableDynamicMixin:
    """Mixin class for creating a dynamic variable class in conjunction with a static class inheriting from BaseVariable, like ScalarVariable or CategoricalVariable."""

    def __init__(
        self,
        config: BaseDynamicVariableConfig,
    ) -> None:
        self._required_variables = config.required_variables if config.required_variables else []
        self._required_ids = self.__extract_all_required_ids(
            required_ids=config.required_ids, required_variables=config.required_variables
        )
        super().__init__(config)

    @property
    def required_ids(self) -> List[str]:
        return self._required_ids

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        self._check_required_ids(dataframe=dataframe)
        return None

    def get_series(self: Variable, dataframe: pd.DataFrame) -> pd.Series:
        if self.id in dataframe:
            return super().get_series(dataframe)
        else:
            raise NotImplementedError(f"'{self.id}' dynamic variable does not create any series")

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        self._check_required_ids(dataframe=dataframe)

    def _check_required_ids(self, dataframe: pd.DataFrame) -> None:
        ids_not_found = set(self._required_ids).difference(list(dataframe.columns))
        if ids_not_found:
            raise ValueError(
                f"Dataframe does not contain the following required IDs: {list(ids_not_found)}. Please review order of generation of dynamic variables."
            )

    def __extract_all_required_ids(
        self,
        required_ids: Optional[List[str]],
        required_variables: Optional[List[Variable]],
    ) -> List[str]:
        required_variables = required_variables if required_variables else []
        required_ids_set = set(required_ids) if required_ids else set()
        for required_variable in required_variables:
            if isinstance(required_variable, VariableDynamicMixin):
                required_ids_set.update(required_variable.required_ids)
            else:
                required_ids_set.add(required_variable.id)
        return list(required_ids_set)
