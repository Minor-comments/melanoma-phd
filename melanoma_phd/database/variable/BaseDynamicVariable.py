from abc import ABC, abstractmethod
from typing import List, Optional

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


class BaseDynamicVariable(BaseVariable):
    """Class for defining just the dynamic variable interface that must be inherited by new child classes in conjunction with a static variable class."""

    def __init__(
        self,
        id: str,
        name: str,
        required_ids: Optional[List[str]] = None,
        required_variables: Optional[List[BaseVariable]] = None,
    ) -> None:
        self._required_variables = required_variables if required_variables else []
        self._required_ids = self.__extract_all_required_ids(
            required_ids=required_ids, required_variables=required_variables
        )
        super().__init__(id=id, name=name)

    @property
    def required_ids(self) -> List[str]:
        return self._required_ids

    @abstractmethod
    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        self._check_required_ids(dataframe=dataframe)
        pass

    def get_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        pass

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        pass

    def _check_required_ids(self, dataframe: pd.DataFrame) -> None:
        ids_not_found = set(self._required_ids).difference(list(dataframe.columns))
        if ids_not_found:
            raise ValueError(
                f"Dataframe does not contain the following required IDs: {list(ids_not_found)}. Please review order of generation of dynamic variables."
            )

    def __extract_all_required_ids(
        self,
        required_ids: Optional[List[str]],
        required_variables: Optional[List[BaseVariable]],
    ) -> List[str]:
        required_variables = required_variables if required_variables else []
        required_ids_set = set(required_ids) if required_ids else set()
        for required_variable in required_variables:
            if isinstance(required_variable, BaseDynamicVariable):
                required_ids_set.update(required_variable.required_ids)
            elif isinstance(required_variable, BaseVariable):
                required_ids_set.add(required_variable.id)
        return list(required_ids_set)
