from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


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
        y_max_value: Optional[float] = None,
        reference_variable_name: Optional[str] = None,
        percentage_values: bool = False,
    ) -> plotly_go.Figure:
        distribution_variable_names = [variable.name for variable in distribution_variables]
        title = f"Distribution of {' / '.join(distribution_variable_names)}"
        plot_kwargs = {"y": "value", "x": "variable"}
        if show_points:
            plot_kwargs["points"] = "all"

        if categorical_variable:
            categorical_variable_name = categorical_variable.name
            categorical_data = categorical_variable.get_series(dataframe)
            plot_df = pd.DataFrame(
                [
                    (value, variable.name, categorical_data.iloc[i])
                    for variable in distribution_variables
                    for i, value in enumerate(variable.get_series(dataframe).values)
                ],
                columns=["value", "variable"] + [categorical_variable_name],
            )
            title += f" over {categorical_variable_name}"
            plot_kwargs.update({"color": categorical_variable_name})
        else:
            plot_df = pd.DataFrame(
                [
                    (value, variable.name)
                    for variable in distribution_variables
                    for value in variable.get_series(dataframe).values
                ],
                columns=["value", "variable"],
            )
        plot_kwargs.update({"title": title})

        fig = px.box(plot_df, **plot_kwargs)

        if reference_variable_name:
            percentage_values = True
            fig.update_yaxes(title=f"Mean (% of {reference_variable_name})")
        elif percentage_values:
            fig.update_yaxes(title=f"Mean (%)")
        else:
            fig.update_yaxes(title=f"Mean")

        if y_max_value:
            fig.update_yaxes(range=[0, y_max_value])

        if categorical_variable:
            xaxis_title = categorical_variable_name
        else:
            xaxis_title = ""
        fig.update_xaxes(title=xaxis_title)
        return fig
