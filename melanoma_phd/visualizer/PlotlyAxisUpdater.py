import math
from dataclasses import dataclass
from typing import List, Optional

import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


@dataclass
class PlotlyAxisUpdaterConfig:
    y_max_value: Optional[float] = None
    reference_variable_name: Optional[str] = None
    percentage_values: bool = False
    categorical_variable: Optional[CategoricalVariable] = None
    distribution_variables: Optional[List[ScalarVariable]] = None
    y_log_axis: bool = False


class PlotlyAxisUpdater:
    @classmethod
    def update_axis(
        self, fig: plotly_go.Figure, config: PlotlyAxisUpdaterConfig
    ) -> plotly_go.Figure:
        if config.distribution_variables and len(config.distribution_variables) == 1:
            yaxes_title = f"{config.distribution_variables[0].name} mean"
        else:
            yaxes_title = "Mean"

        if config.reference_variable_name:
            yaxes_title += f" (% of {config.reference_variable_name})"
        elif config.percentage_values:
            yaxes_title += f" (%)"
        fig.update_yaxes(title=yaxes_title)

        if config.y_log_axis:
            fig.update_yaxes(type="log")

        if config.y_max_value:
            fig.update_yaxes(
                range=[
                    0,
                    math.log10(config.y_max_value) if config.y_log_axis else config.y_max_value,
                ]
            )

        if config.categorical_variable:
            xaxis_title = config.categorical_variable.name
        else:
            xaxis_title = ""
        fig.update_xaxes(title=xaxis_title)

        return fig
