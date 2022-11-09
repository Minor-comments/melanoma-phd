from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any


class OutlierMethod(Enum):
    STD = auto()
    IQR = auto()
    Z_SCORE_MODIFIED = auto()


class BaseFigure(ABC):
    """Base class representing all possible figures to create for being plotted in Streamlit."""

    @abstractmethod
    def create_figure(self) -> Any:
        pass

    # @abstractmethod
    # def _check_input_data_consistency(self) -> None:
    #     pass

    # @staticmethod
    # def get_number_of_bins(
    #    data: Union[pd.Series, np.array, List[Union[int, float]]], min_bins: int = 0
    # ) -> int:
    #    length = len(data)
    #    if length <= min_bins:
    #        return length


#
#    if isinstance(data, pd.Series):
#        n_unique = data.nunique()
#    elif isinstance(data, np.array) or isinstance(data, list):
#        n_unique = len(np.unique(data))
#    else:
#        raise ValueError(f"Unsupported data type: {type(data)}")
#
#    bins = 1 + 3.322 * np.log(length)  # Sturge’s Rule
#    # bins = length ** (1 / 3)       # Rice's Rule
#    return min(n_unique, max(min_bins, int(bins)))
#
# @staticmethod
# def get_outliers_mask(
#    data: Union[pd.Series, np.array, List[Union[int, float]]],
#    outlier_method: OutlierMethod = OutlierMethod.IQR,
# ) -> np.array:
#    if isinstance(data, pd.Series):
#        data = data.values
#    elif isinstance(data, list):
#        data = np.array(data)
#    elif isinstance(data, np.array):
#        pass
#    else:
#        raise ValueError(f"Unsupported data type: {type(data)}")
#
#    if outlier_method == OutlierMethod.IQR:
#        q3, q1 = np.percentile(data, [75, 25])
#        IQR = q3 - q1
#        upper_bound = q3 + 1.5 * IQR
#        lower_bound = q1 - 1.5 * IQR
#        outliers_mask = (data > upper_bound) | (data < lower_bound)
#    elif outlier_method == OutlierMethod.STD:
#        outliers_mask = np.abs(data - data.mean()) > 3 * data.std()
#    elif outlier_method == OutlierMethod.Z_SCORE_MODIFIED:
#        outliers_mask = (0.6745 * np.abs(data - data.mean()) / np.median(data)) > 3.5
#    return outliers_mask
