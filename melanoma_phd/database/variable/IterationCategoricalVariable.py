from typing import Dict, List, Optional, Union

import pandas as pd

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.IteratedCategoricalVariableStatic import (
    IteratedCategoricalVariableStatic,
)
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable
from melanoma_phd.database.variable.VariableDynamicMixin import (
    BaseDynamicVariableConfig,
    VariableDynamicMixin,
)


class IterationCategoricalVariableConfig(BaseDynamicVariableConfig):
    def __init__(
        self,
        id: str,
        name: str,
        categories: Optional[Dict[Union[int, float, str], str]],
        reference_variable: ReferenceIterationVariable,
        iterated_variables: List[IteratedCategoricalVariableStatic],
        selectable: bool = True,
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            selectable=selectable,
        )
        self.categories = categories
        self.reference_variable = reference_variable
        self.iterated_variables = iterated_variables


class IterationCategoricalVariable(VariableDynamicMixin, CategoricalVariable):
    def __init__(self, config: IterationCategoricalVariableConfig) -> None:
        super().__init__(config=config)
        self._iterated_variables = config.iterated_variables
        self._reference_variable = config.reference_variable

    @property
    def reference_variable(self):
        return self._reference_variable

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    def create_new_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        return self.get_series(dataframe=dataframe).dropna()

    def get_series(self, dataframe: pd.DataFrame) -> pd.Series:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        series = pd.Series(
            dataframe[iterated_variable_ids].mode(axis=1).iloc[:, 0],
            index=dataframe.index,
            name=self.id,
        )
        return series

    def filter(self, dataframe: pd.DataFrame, filter_dataframe: pd.DataFrame) -> pd.DataFrame:
        iterated_variable_ids = [varable.id for varable in self._iterated_variables]
        iterated_filter_dataframe = filter_dataframe.copy()
        iterated_filter_dataframe.columns = iterated_variable_ids
        filtered_dataframe = dataframe.copy()
        for iterated_variable_id in iterated_variable_ids:
            filtered_dataframe.loc[:, iterated_variable_id].where(
                iterated_filter_dataframe[iterated_variable_id], inplace=True
            )
        filtered_dataframe[self.id] = self.get_series(dataframe=filtered_dataframe)
        return filtered_dataframe

    def get_filter_dataframe(
        self, dataframe: pd.DataFrame, category_options: List[str]
    ) -> pd.DataFrame:
        filter_dataframe = dataframe.loc[:, [variable.id for variable in self._iterated_variables]]
        return filter_dataframe.isin(self.get_category_values(category_options))
