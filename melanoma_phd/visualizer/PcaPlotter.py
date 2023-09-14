from typing import Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.statistics.PcaProcessor import PcaProcessorResult
from melanoma_phd.database.variable.BaseVariable import BaseVariable


class PcaPlotter:
    def plot_importance(self, pca_result: PcaProcessorResult) -> plotly_go.Figure:
        labels = self.__generate_labels(pca_result)
        title = f"PCA feature importance<br>{self.__generate_explained_variance_title(pca_result)}"
        fig = px.scatter(
            pca_result.importance,
            x="PC1",
            y="PC2",
            labels=labels,
            title=title,
        )
        fig.add_traces(
            [
                plotly_go.Line(
                    x=[0, pca_values["PC1"]],
                    y=[0, pca_values["PC2"]],
                    text=variable_name,
                    name=variable_name,
                )
                for variable_name, pca_values in pca_result.importance.T.items()
            ]
        )
        return fig

    def plot_pca(
        self,
        pca_result: PcaProcessorResult,
        df: pd.DataFrame,
        legend_variables: Optional[List[Optional[BaseVariable]]] = None,
    ) -> plotly_go.Figure:
        if not legend_variables:
            legend_variables = [None]

        for legend_variable in legend_variables:
            if legend_variable:
                color = legend_variable.get_series(df).loc[pca_result.pca_df.index]
            else:
                color = None

        labels = self.__generate_labels(pca_result)
        title = f"Patient PCA<br>{self.__generate_explained_variance_title(pca_result)}"

        fig = px.scatter(
            pca_result.components,
            x="PC1",
            y="PC2",
            labels=labels,
            color=color,
            title=title,
            hover_name=pd.Series(pca_result.components.index).apply(lambda x: f"Patient {x}"),
        )
        return fig

    def __generate_labels(self, pca_result: PcaProcessorResult) -> Dict[str, str]:
        return {
            f"PC{i+1}": f"PC{i+1} ({var:.1f}%)"
            for i, var in enumerate(pca_result.explained_variance_ratio * 100)
        }

    def __generate_explained_variance_title(self, pca_result: PcaProcessorResult) -> str:
        return f"Total Explained Variance: {pca_result.explained_variance_ratio.sum() * 100:.2f}%"
