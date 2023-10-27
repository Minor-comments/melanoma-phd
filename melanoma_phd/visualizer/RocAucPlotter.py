import plotly.graph_objects as go

from melanoma_phd.database.statistics.TrainingModel import TrainingModelResult


class RocAucPlotter:
    def plot(self, results: TrainingModelResult) -> go.Figure:
        c_fill = "rgba(52, 152, 219, 0.2)"
        c_line = "rgba(52, 152, 219, 0.5)"
        c_line_main = "rgba(41, 128, 185, 1.0)"
        c_grid = "rgba(189, 195, 199, 0.5)"
        c_annot = "rgba(149, 165, 166, 0.5)"
        c_highlight = "rgba(192, 57, 43, 1.0)"

        fig = go.Figure(
            [
                go.Scatter(
                    x=results.fpr_mean,
                    y=results.tpr_upper,
                    line=dict(color=c_line, width=1),
                    hoverinfo="skip",
                    showlegend=False,
                    name="upper",
                ),
                go.Scatter(
                    x=results.fpr_mean,
                    y=results.tpr_lower,
                    fill="tonexty",
                    fillcolor=c_fill,
                    line=dict(color=c_line, width=1),
                    hoverinfo="skip",
                    showlegend=False,
                    name="lower",
                ),
                go.Scatter(
                    x=results.fpr_mean,
                    y=results.tpr_mean,
                    line=dict(color=c_line_main, width=2),
                    hoverinfo="skip",
                    showlegend=True,
                    name=f"AUC: {results.metrics.loc['Mean', 'AUC']:.3%}",
                ),
            ]
        )
        fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)
        fig.update_layout(
            template="plotly_white",
            title_x=0.5,
            xaxis_title="1 - Specificity",
            yaxis_title="Sensitivity",
            width=800,
            height=800,
            legend=dict(
                yanchor="bottom",
                xanchor="right",
                x=0.95,
                y=0.01,
            ),
        )
        fig.update_yaxes(
            range=[0, 1], gridcolor=c_grid, scaleanchor="x", scaleratio=1, linecolor="black"
        )
        fig.update_xaxes(range=[0, 1], gridcolor=c_grid, constrain="domain", linecolor="black")
        return fig
