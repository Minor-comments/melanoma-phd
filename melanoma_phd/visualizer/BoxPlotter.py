from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.RemainingDistributionVariable import (
    RemainingDistributionVariable,
    RemainingDistributionVariableConfig,
)
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.DistributionPlotterHelper import DistributionPlotterHelper
from melanoma_phd.visualizer.PlotlyAxisUpdater import PlotlyAxisUpdater, PlotlyAxisUpdaterConfig


class BoxPlotter:
    def __init__(
        self,
    ) -> None:
        pass

    def plot(
        self,
        distribution_variables: List[ScalarVariable],
        dataframe: pd.DataFrame,
        categorical_variable: Optional[CategoricalVariable] = None,
        show_points: bool = False,
        axis_config: Optional[PlotlyAxisUpdaterConfig] = None,
    ) -> plotly_go.Figure:
        distribution_plotter_helper = DistributionPlotterHelper(
            distribution_variables=distribution_variables,
        )

        plot_kwargs = {"y": "value", "x": "variable"}
        if show_points:
            plot_kwargs["points"] = "all"

        distribution_variable_lengths = [
            len(variable.get_series(dataframe)) for variable in distribution_variables
        ]

        if categorical_variable:
            categorical_variable_name = categorical_variable.name
            categorical_data = categorical_variable.get_series(dataframe)
            plot_df = pd.DataFrame(
                [
                    (
                        value,
                        distribution_plotter_helper.generate_variable_name_with_n_size(
                            variable_index=i,
                            n=distribution_variable_lengths[i],
                        ),
                        categorical_data.iloc[j],
                    )
                    for i, variable in enumerate(distribution_variables)
                    for j, value in enumerate(variable.get_series(dataframe).values)
                ],
                columns=["value", "variable"] + [categorical_variable_name],
            )
            plot_kwargs.update({"color": categorical_variable_name})
        else:
            plot_df = pd.DataFrame(
                [
                    (
                        value,
                        distribution_plotter_helper.generate_variable_name_with_n_size(
                            variable_index=i,
                            n=distribution_variable_lengths[i],
                        ),
                    )
                    for i, variable in enumerate(distribution_variables)
                    for value in variable.get_series(dataframe).values
                ],
                columns=["value", "variable"],
            )

        title = distribution_plotter_helper.generate_title(categorical_variable)
        plot_kwargs.update({"title": title})

        fig = px.box(plot_df, **plot_kwargs)

        if axis_config:
            fig = PlotlyAxisUpdater.update_axis(fig, axis_config)

        return fig
