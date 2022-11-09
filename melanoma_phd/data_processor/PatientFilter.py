from dataclasses import dataclass
from typing import List

from melanoma_phd.database.PopulationGroup import PopulationGroup
from melanoma_phd.database.TreatmentType import TreatmentType


@dataclass
class PatientFilter:
    population_groups: List[PopulationGroup] = None
    current_treatment_types: List[TreatmentType] = None
