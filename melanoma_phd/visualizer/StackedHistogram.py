from typing import List

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
        all_variables = distribution_variables + [categorical_variable]
        distribution_variable_names = [variable.name for variable in distribution_variables]
        categorical_variable_name = categorical_variable.name
        plot_df = pd.DataFrame(
            zip(
                *[variable.get_series(dataframe) for variable in all_variables],
            ),
            columns=distribution_variable_names + [categorical_variable_name],
        )

        title = f"Distribution of {' / '.join(distribution_variable_names)} over {categorical_variable_name}"

        fig = px.histogram(
            plot_df,
            x=categorical_variable_name,
            y=distribution_variable_names,
            title=title,
            histfunc="avg",
        )
        return fig
