from enum import Enum


class StatisticFieldName(Enum):
    COUNT = "n"
    MEDIAN = "median"
    MEAN = "mean"
    STD_DEVIATION = "std"
    QUARTILE_1 = "Q1"
    QUARTILE_3 = "Q3"
    MIN_VALUE = "min"
    MAX_VALUE = "max"
    PERCENTAGE = "%"
