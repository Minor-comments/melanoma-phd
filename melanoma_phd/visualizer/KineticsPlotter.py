from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from melanoma_phd.database.Patient import Patient
from melanoma_phd.database.variable.IterationScalarVariable import IterationScalarVariable


class KineticsPlotter:
    def __init__(self) -> None:
        pass

    def plot(self, variable: IterationScalarVariable, patients: List[Patient]) -> plt.Figure:
        time_series: Dict[str, pd.DataFrame] = {}
        for patient in patients:
            time_series[patient.id] = patient.create_time_series(
                time_variable_name="TIEMPO IT{N}",
                value_variable_name=variable.id,
                range=list(range(1, 11, 1)),
            )
        fig, axes = plt.subplots(1, 1)
        for patient_id, ts in time_series.items():
            lines = axes.plot(ts.iloc[:, 0], ts.iloc[:, 1], "o-")
            lines[0].set_label(patient_id)
        axes.set_xlabel("Months")
        axes.set_ylabel(variable.name)
        axes.grid(True)
        axes.legend()

        return fig
