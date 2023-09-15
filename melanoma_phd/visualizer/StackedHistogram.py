from collections import defaultdict
from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.ColorGenerator import ColorGenerator
from melanoma_phd.visualizer.DistributionPlotterHelper import DistributionPlotterHelper
from melanoma_phd.visualizer.PlotlyAxisUpdater import PlotlyAxisUpdater, PlotlyAxisUpdaterConfig


class StackedHistogram:
    def __init__(self, color_generator: Optional[ColorGenerator] = None) -> None:
        self._color_generator = color_generator

    def plot(
        self,
        distribution_variables: List[ScalarVariable],
        categorical_variable: CategoricalVariable,
        dataframe: pd.DataFrame,
        axis_config: Optional[PlotlyAxisUpdaterConfig] = None,
    ) -> plotly_go.Figure:
        distribution_variables = sorted(distribution_variables, key=lambda variable: variable.name)
        data = []
        for variable in distribution_variables + [categorical_variable]:
            serie = variable.get_series(dataframe)
            serie.name = variable.name
            data.append(serie)
        plot_df = pd.concat(data, axis=1)

        distribution_variable_names = [variable.name for variable in distribution_variables]
        categorical_variable_name = categorical_variable.name
        categorical_unique_data = list(categorical_variable.get_series(dataframe).unique())
        if len(categorical_unique_data) > 1:
            categorical_unique_data += ["All"]

        fig = plotly_go.Figure()
        color_samples = (
            self._color_generator.generate(distribution_variable_names)
            if self._color_generator
            else None
        )
        not_null_mask = plot_df[distribution_variable_names].notnull().all(axis=1)
        for index, name in enumerate(distribution_variable_names):
            minus_errors = []
            means = []
            x_names = []
            for category_name in categorical_unique_data:
                if category_name == "All":
                    filtered_df = plot_df[not_null_mask]
                else:
                    filtered_df = plot_df[
                        (plot_df[categorical_variable_name] == category_name) & (not_null_mask)
                    ]
                minus_errors.append(float(np.nanstd(filtered_df[name]) / 2))
                means.append(float(np.nanmean(filtered_df[name])))
                x_names.append(f"{category_name}<br>N = {len(filtered_df)}")

            hovertemplate = (
                f"variable: {name}<br>" + f"{categorical_variable_name}: %{{x}}<br>"
                "value: %{y:.3f}<extra></extra>"
            )
            fig.add_trace(
                plotly_go.Bar(
                    name=name,
                    x=x_names,
                    y=means,
                    hovertemplate=hovertemplate,
                    error_y={
                        "type": "data",
                        "symmetric": False,
                        "arrayminus": minus_errors,
                        "array": [
                            0,
                        ]
                        * len(minus_errors),
                    },
                    marker={
                        "color": color_samples[index] if color_samples else None,
                    },
                )
            )

        distribution_plotter_helper = DistributionPlotterHelper(
            distribution_variables=distribution_variables,
        )

        title = distribution_plotter_helper.generate_title(categorical_variable)
        fig.update_layout(
            barmode="stack",
            title=title,
            legend_title="variable",
            hoverlabel_align="left",
        )

        if axis_config:
            fig = PlotlyAxisUpdater.update_axis(fig, axis_config)

        return fig
