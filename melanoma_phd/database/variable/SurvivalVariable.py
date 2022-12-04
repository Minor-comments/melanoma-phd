import pandas as pd
from sksurv.nonparametric import SurvivalFunctionEstimator
from sksurv.util import Surv

from melanoma_phd.database.variable.BaseDynamicVariable import \
    BaseDynamicVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class SurvivalVariable(ScalarVariable, BaseDynamicVariable):
    def __init__(
        self,
        id: str,
        name: str,
        duration_variable_id: str,
        events_variable_id: str,
    ) -> None:
        super().__init__(id=id, name=name)
        self._duration_variable_id = duration_variable_id
        self._events_variable_id = events_variable_id

    def init_from_dataframe(self, dataframe: pd.DataFrame) -> None:
        super().init_from_dataframe(dataframe=dataframe)

    def create_new_series(self, dataframe: pd.DataFrame) -> pd.Series:
        estimator = SurvivalFunctionEstimator()
        events = (dataframe[self._events_variable_id].dropna() != 0).to_numpy()
        durations = dataframe[self._duration_variable_id].dropna().to_numpy()
        estimator.fit(Surv.from_arrays(events, durations))
        return dataframe[self._duration_variable_id].map(
            lambda value: estimator.predict_proba([value])[0], na_action="ignore"
        )

    def descriptive_statistics(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return super().descriptive_statistics(dataframe=dataframe)

    def _check_valid_id(self, dataframe: pd.DataFrame) -> None:
        return super()._check_valid_id(dataframe)
