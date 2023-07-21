from collections import defaultdict
from typing import List, Optional

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
        y_max_value: Optional[float] = None,
        reference_variable_name: Optional[str] = None,
        percentage_values: bool = False,
    ) -> plotly_go.Figure:
        distribution_data = [
            variable.get_series(dataframe).values for variable in distribution_variables
        ]
        distribution_variable_names = [variable.name for variable in distribution_variables]
        categorical_variable_name = categorical_variable.name
        categorical_data = categorical_variable.get_series(dataframe)
        categorical_unique_data = list(categorical_data.unique()) + ["All"]
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
            minus_errors = []
            means = []
            x_names = []
            for category_name in categorical_unique_data:
                if category_name == "All":
                    filtered_df = plot_df
                else:
                    filtered_df = plot_df[plot_df[categorical_variable_name] == category_name]
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

        if reference_variable_name:
            percentage_values = True
            fig.update_yaxes(title=f"Mean (% of {reference_variable_name})")
        elif percentage_values:
            fig.update_yaxes(title=f"Mean (%)")
        else:
            fig.update_yaxes(title=f"Mean")

        if y_max_value:
            fig.update_yaxes(range=[0, y_max_value])

        return fig
