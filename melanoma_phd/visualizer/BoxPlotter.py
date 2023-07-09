from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class BoxPlotter:
    def __init__(self) -> None:
        pass

    def plot(
        self,
        distribution_variables: List[ScalarVariable],
        dataframe: pd.DataFrame,
        categorical_variable: Optional[CategoricalVariable] = None,
    ) -> plotly_go.Figure:
        distribution_variable_names = [variable.name for variable in distribution_variables]
        title = f"Distribution of {' / '.join(distribution_variable_names)}"
        plot_kwargs = {"y": "value", "x": "variable"}
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
        return fig
