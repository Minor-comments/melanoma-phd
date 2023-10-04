from copy import deepcopy
from typing import List, Optional

import pandas as pd
from sklearn.preprocessing import PowerTransformer


class PreProcessor:
    def __init__(
        self, transform_floats: bool = True, substring_transform_columns: Optional[List[str]] = None
    ):
        self._transform_floats = transform_floats
        self._substring_transform_columns = (
            substring_transform_columns if substring_transform_columns else []
        )

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        new_df = deepcopy(df)

        if self._transform_floats:
            columns_to_transform = new_df.dtypes.astype(str).str.startswith("float")
        else:
            columns_to_transform = pd.Series(False, index=new_df.columns)

        for log_column_substring in self._substring_transform_columns:
            columns_to_transform |= new_df.columns.str.contains(log_column_substring)

        new_df.loc[:, columns_to_transform] = PowerTransformer().fit_transform(
            new_df.loc[:, columns_to_transform]
        )

        return new_df
