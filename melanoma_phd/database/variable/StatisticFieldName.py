from enum import Enum


class StatisticFieldName(Enum):
    COUNT = "n"
    MEDIAN = "median"
    MEAN = "mean"
    STD_DEVIATION = "std"
    MIN_VALUE = "min"
    MAX_VALUE = "max"
    PERCENTAGE = "%"
