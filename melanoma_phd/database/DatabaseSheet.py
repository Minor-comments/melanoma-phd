from dataclasses import dataclass
from typing import List

import pandas as pd

from melanoma_phd.database.variable.BaseVariable import BaseVariable


@dataclass
class DatabaseSheet:
    name: str
    dataframe: pd.DataFrame
    variables: List[BaseVariable]
