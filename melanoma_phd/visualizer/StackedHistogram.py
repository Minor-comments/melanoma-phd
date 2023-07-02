from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable


class StackedHistogram:
    def __init__(self) -> None:
        pass

    def plot(
        self,
        distribution_variables: List[ScalarVariable],
        categorical_variable: CategoricalVariable,
        dataframe: pd.DataFrame,
    ) -> plotly_go.Figure:
        distribution_data = [
            variable.get_series(dataframe).values for variable in distribution_variables
        ]
        distribution_variable_names = [variable.name for variable in distribution_variables]
        categorical_variable_name = categorical_variable.name
        categorical_data = categorical_variable.get_series(dataframe)
        categorical_unique_data = categorical_data.unique()
        plot_df = pd.DataFrame(
            zip(*distribution_data, categorical_data),
            columns=distribution_variable_names + [categorical_variable_name],
            index=categorical_data.index,
        )

        errors_by_category = defaultdict(dict)
        for category_name, grouped_by_data in plot_df.groupby(categorical_variable_name):
            for distribution_variable_name in distribution_variable_names:
                errors_by_category[distribution_variable_name][category_name] = float(
                    np.nanstd(grouped_by_data[distribution_variable_name])
                )

        title = f"Distribution of {' / '.join(distribution_variable_names)} over {categorical_variable_name}"

        fig = plotly_go.Figure()
        for name in distribution_variable_names:
            errors = []
            means = []
            for category_name in categorical_unique_data:
                filtered_df = plot_df[plot_df[categorical_variable_name] == category_name]
                errors.append(float(np.nanstd(filtered_df[name])))
                means.append(float(np.nanmean(filtered_df[name])))

            hovertemplate = (
                f"variable: {name}<br>" + f"{categorical_variable_name}: %{{x}}<br>"
                "value: %{y:.3f}<extra></extra>"
            )
            fig.add_trace(
                plotly_go.Bar(
                    name=name,
                    x=categorical_unique_data,
                    y=means,
                    hovertemplate=hovertemplate,
                    error_y={"type": "data", "array": errors},
                )
            )
        fig.update_layout(
            barmode="stack",
            title=title,
            xaxis_title=categorical_variable_name,
            legend_title="variable",
            hoverlabel_align="left",
            yaxis_title="Mean value",
        )
        return fig
