from dataclasses import dataclass

from melanoma_phd.database.variable.BaseVariable import VariableStatisticalType


@dataclass
class VariableStatisticalProperties:
    type: VariableStatisticalType
    normality: bool
