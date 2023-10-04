import enum
from typing import Dict, List, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objs as plotly_go

from melanoma_phd.database.statistics.PcaProcessor import PcaProcessorResult
from melanoma_phd.database.variable.BaseVariable import BaseVariable


class PcaPlotter:
    def plot_importance(self, pca_result: PcaProcessorResult) -> Optional[plotly_go.Figure]:
        if pca_result.importance is not None:
            labels = self.__generate_labels(pca_result)
            title = (
                f"PCA feature importance<br>{self.__generate_explained_variance_title(pca_result)}"
            )

            plot_kwargs = dict(
                data_frame=pca_result.importance,
                x="PC1",
                y="PC2",
                labels=labels,
                title=title,
                hover_name=pca_result.importance.index,
            )
            if len(pca_result.importance.columns) == 2:
                fig = px.scatter(**plot_kwargs)
                fig.add_traces(
                    [
                        plotly_go.Scatter(
                            x=[0, pca_values["PC1"]],
                            y=[0, pca_values["PC2"]],
                            name=variable_name,
                            hoverinfo="skip",
                            mode="lines",
                        )
                        for variable_name, pca_values in pca_result.importance.T.items()
                    ]
                )
            elif len(pca_result.importance.columns) == 3:
                fig = px.scatter_3d(z="PC3", **plot_kwargs)
                fig.add_traces(
                    [
                        plotly_go.Scatter3d(
                            x=[0, pca_values["PC1"]],
                            y=[0, pca_values["PC2"]],
                            z=[0, pca_values["PC3"]],
                            name=variable_name,
                            hoverinfo="skip",
                            mode="lines",
                        )
                        for variable_name, pca_values in pca_result.importance.T.items()
                    ]
                )
            else:
                raise ValueError(
                    f"PCA feature importance cannot be plotted with {len(pca_result.importance.columns)} components"
                )
            return fig
        return None

    def plot_pca(
        self,
        pca_result: PcaProcessorResult,
        df: pd.DataFrame,
        legend_variables: Optional[List[BaseVariable]] = None,
    ) -> List[plotly_go.Figure]:
        if not legend_variables:
            legend_variables = [None]

        figures = []
        for legend_variable in legend_variables:
            labels = self.__generate_labels(pca_result)
            title = f"Patient PCA{f' by {legend_variable.name}' if legend_variable else ''}<br>{self.__generate_explained_variance_title(pca_result)}"

            if legend_variable:
                color = legend_variable.get_series(df).loc[pca_result.pca_df.index]
                labels["color"] = legend_variable.name
            else:
                color = None

            plot_kwargs = dict(
                labels=labels,
                color=color,
                title=title,
                hover_name=pd.Series(pca_result.components.index).apply(lambda x: f"Patient {x}"),
            )
            if len(pca_result.components.columns) == 2:
                fig = px.scatter(
                    pca_result.components,
                    x="PC1",
                    y="PC2",
                    **plot_kwargs,
                )
            elif len(pca_result.components.columns) == 3:
                fig = px.scatter_3d(pca_result.components, x="PC1", y="PC2", z="PC3", **plot_kwargs)
            else:
                raise ValueError(
                    f"Using {len(pca_result.components.columns)} components it is not supported"
                )
            figures.append(fig)
        return figures

    def __generate_labels(self, pca_result: PcaProcessorResult) -> Dict[str, str]:
        labels = {
            f"PC{i+1}": f"PC{i+1} ({var:.1f}%)"
            for i, var in enumerate(pca_result.explained_variance_ratio * 100)
        }
        labels.update({"xyz"[i]: value for i, value in enumerate(labels.values())})
        return labels

    def __generate_explained_variance_title(self, pca_result: PcaProcessorResult) -> str:
        return f"Total Explained Variance: {pca_result.explained_variance_ratio.sum() * 100:.2f}%"
