from copy import deepcopy
from typing import List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
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

        plot_kwargs = {"y": "value"}
        if show_points:
            plot_kwargs["points"] = "all"

        if categorical_variable:
            categorical_variable_name = categorical_variable.name
            categorical_data = categorical_variable.get_series(dataframe)
            plot_df = pd.DataFrame(
                [
                    (
                        value,
                        variable.name if len(distribution_variables) > 1 else "",
                        categorical_data.iloc[j],
                    )
                    for i, variable in enumerate(distribution_variables)
                    for j, value in enumerate(variable.get_series(dataframe).values)
                ],
                columns=["value", "variable"] + [categorical_variable_name],
            )
            if categorical_data.nunique() > 1:
                plot_df_all = deepcopy(plot_df)
                plot_df_all[categorical_variable_name] = "All"
                plot_df = pd.concat([plot_df, plot_df_all], ignore_index=True).reset_index(
                    drop=True
                )
            plot_kwargs.update(
                {
                    "color": categorical_variable_name,
                    "facet_col": "variable",
                    "x": categorical_variable_name,
                }
            )
        else:
            plot_df = pd.DataFrame(
                [
                    (
                        value,
                        variable.name if len(distribution_variables) > 1 else "",
                    )
                    for i, variable in enumerate(distribution_variables)
                    for value in variable.get_series(dataframe).values
                ],
                columns=["value", "variable"],
            )
            plot_kwargs.update({"x": "variable"})

        title = distribution_plotter_helper.generate_title(categorical_variable)
        plot_kwargs.update({"title": title})

        fig = px.box(plot_df, **plot_kwargs)

        if axis_config:
            fig = PlotlyAxisUpdater.update_axis(fig, axis_config)

        count_group_by = ["variable"]
        if categorical_variable:
            count_group_by.append(categorical_variable_name)
        count_dict = plot_df.groupby(count_group_by)["value"].count().to_dict()
        yshift = (
            -(
                axis_config.y_max_value
                if axis_config and axis_config.y_max_value
                else plot_df["value"].max()
            )
            // 5
        )

        annotation_kwargs = dict(
            xanchor="center",
            y=min(0, plot_df["value"].max()),
            yshift=yshift,
            showarrow=False,
        )
        if categorical_variable:
            for i in range(len(fig.layout["annotations"])):
                variable_name = fig.layout["annotations"][i]["text"].replace("variable=", "")
                fig.layout["annotations"][i]["text"] = fig.layout["annotations"][i]["text"].replace(
                    "variable=", ""
                )

                xaxis_index = f"{i+1 if i != 0 else ''}"
                for count_key, count in count_dict.items():
                    count_variable_name = count_key[0]
                    if variable_name == count_variable_name:
                        categories = fig.layout["xaxis" + xaxis_index]["categoryarray"]
                        x = self.__calculate_x_annotation(
                            category_index=categories.index(count_key[1]),
                            num_categories=len(categories),
                        )

                        fig.add_annotation(
                            xref=f"x{xaxis_index} domain",
                            axref=f"x{xaxis_index} domain",
                            x=x,
                            text=f"N = {count}",
                            **annotation_kwargs,
                        )
        else:
            distribution_variable_names = [variable.name for variable in distribution_variables]
            for i, count_variable_name in enumerate(distribution_variable_names):
                count = count_dict[count_variable_name]
                x = self.__calculate_x_annotation(
                    category_index=i,
                    num_categories=len(distribution_variables),
                )

                fig.add_annotation(
                    xref=f"x domain",
                    axref=f"x domain",
                    x=x,
                    text=f"N = {count}",
                    **annotation_kwargs,
                )

        return fig

    def __calculate_x_annotation(self, category_index: int, num_categories: int) -> float:
        x = 0.5
        distances_center = float(category_index - num_categories // 2)
        if num_categories % 2 == 0:
            distances_center += 0.5

        if distances_center:
            x += distances_center / num_categories
        return x
