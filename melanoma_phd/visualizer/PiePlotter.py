from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.database.variable.StatisticFieldName import StatisticFieldName


class PiePlotter:
    def __init__(self) -> None:
        pass

    def plot(self, variable_statistics: Dict[ScalarVariable, pd.DataFrame]) -> plt.Figure:
        labels, sizes = self.__get_variable_labels_sizes(variable_statistics)
        colors = [
            "#9BBFE0",
            "#E8A09A",
            "#FBE29F",
            "#C6D68F",
            "#809bce",
            "#d6eadf",
            "#eac4d5",
            "#fcf5c7",
        ]
        figure, axes = plt.subplots()
        wedges, _, _ = axes.pie(
            x=sizes, labels=None, autopct="%1.1f%%", startangle=90, colors=colors
        )
        axes.axis("equal")
        plt.legend(wedges, labels, loc="lower right", bbox_to_anchor=(1.25, -0.30))
        return figure

    def __get_variable_labels_sizes(
        self, variable_statistics: Dict[ScalarVariable, pd.DataFrame]
    ) -> Tuple[List[str], List[float]]:
        labels = [variable.name for variable in variable_statistics.keys()]
        sizes = [
            statistics.loc[0][StatisticFieldName.MEAN.value]
            for statistics in variable_statistics.values()
        ]
        sum_size = sum(sizes)
        if sum_size < 100:
            labels.append("Others")
            sizes.append(100.0 - sum_size)

        return (labels, sizes)
