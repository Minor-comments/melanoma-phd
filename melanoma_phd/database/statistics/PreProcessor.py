from copy import deepcopy
from enum import Enum, auto
from typing import List, Optional

import pandas as pd
from sklearn.preprocessing import PowerTransformer


class NanTreatment(Enum):
    KEEP_AS_VALID_VALUE = auto()
    DROP = auto()


class PreProcessor:
    def __init__(
        self,
        transform_floats: bool = True,
        substring_transform_columns: Optional[List[str]] = None,
    ):
        self._transform_floats = transform_floats
        self._substring_transform_columns = (
            substring_transform_columns if substring_transform_columns else []
        )

    def preprocess(
        self, df: pd.DataFrame, nan_treatment: Optional[NanTreatment] = None
    ) -> pd.DataFrame:
        new_df = deepcopy(df)

        if len(new_df.index) > 0:
            if self._transform_floats:
                columns_to_transform = new_df.dtypes.astype(str).str.startswith("float")
            else:
                columns_to_transform = pd.Series(False, index=new_df.columns)

            for log_column_substring in self._substring_transform_columns:
                columns_to_transform |= new_df.columns.astype(str).str.contains(
                    log_column_substring
                )

            if columns_to_transform.any():
                new_df.loc[:, columns_to_transform] = PowerTransformer().fit_transform(
                    new_df.loc[:, columns_to_transform]
                )

            if not columns_to_transform.all():
                if nan_treatment == NanTreatment.KEEP_AS_VALID_VALUE:
                    new_df.loc[:, ~columns_to_transform] = new_df.loc[
                        :, ~columns_to_transform
                    ].fillna("NA")

            if nan_treatment == NanTreatment.DROP:
                new_df = new_df.loc[:, ~columns_to_transform].dropna()

        return new_df
