from typing import List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import pandas as pd
from lifelines.statistics import StatisticalResult
from lifelines.plotting import add_at_risk_counts
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.SurvivalVariable import SurvivalVariable


class SurvivalFunctionPlotter:
    def __init__(self, survival_variable: SurvivalVariable) -> None:
        self._survival_variable = survival_variable

    def plot(
        self,
        dataframe: pd.DataFrame,
        group_by: Optional[Union[BaseVariable, List[BaseVariable]]] = None,
        alpha: float = 0.05,
        figsize: Tuple[int, int] = (10, 6),
        confident_interval: bool = True,
        logx: bool = False,
        at_risk_counts: bool = True,
        show_censors: bool = True,
    ) -> plt.Figure:
        if isinstance(group_by, list):
            raise NotImplementedError(
                f"Group by list of variables is not implemented on {self.__class__.__name__}"
            )

        group_by_data = group_by.get_series(dataframe=dataframe) if group_by else None
        group_by_id = group_by.id if group_by else None

        labels = self._survival_variable.get_labels(
            group_by_data=group_by_data
        )

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)

        statistical_result = self._survival_variable.get_logrank_test_stats(
            dataframe=dataframe, group_by_data=group_by_data, alpha=alpha
        )
        title = self.__generate_title(statistical_result=statistical_result)
        plt.title(title)

        kaplan_meier_fitters = self._survival_variable.calculate_kaplan_meier_fitters(
            dataframe=dataframe,
            group_by_data=group_by_data,
            group_by_id=group_by_id,
            alpha=alpha,
        )

        for i, kaplan_meier_fitter in enumerate(kaplan_meier_fitters):
            shown_label = self._survival_variable.get_shown_label(
                label=labels[i], labels=labels, group_by_id=group_by_id
            )

            kaplan_meier_fitter.plot_survival_function(
                ax=ax,
                label=shown_label,
                show_censors=show_censors,
                at_risk_counts=False,
                logx=logx,
                ci_show=confident_interval,
            )

        if at_risk_counts:
            add_at_risk_counts(*kaplan_meier_fitters, ax=ax)

        if len(kaplan_meier_fitters) == 1:
            ax.get_legend().remove()

        return fig

    def __generate_title(self, statistical_result: Optional[StatisticalResult]) -> str:
        title = "Survival function"
        if statistical_result is not None:
            title += "\nLogrank P-Value = %.5f" % (statistical_result.p_value)
        return title
