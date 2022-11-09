from dataclasses import dataclass
from typing import List

import pandas as pd
from melanoma_phd.database.Variable import BaseVariable


@dataclass
class DatabaseSheet:
    name: str
    dataframe: pd.DataFrame
    variables_to_analyze: List[BaseVariable]
