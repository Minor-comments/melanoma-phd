from enum import Enum


class PopulationGroup(Enum):
    RC = (1, "RC con/sin BRAF/MEK")
    ANTI_PD1_CONT = (2, "RC con/sin BRAF/MEK")
    ANTI_PD1_STOP = (3, ">2a antiPD1 ttm STOP")
    PROGRESSION = (4, "Progresión")
    TTM_CONT = (5, ">6-12 meses ttm continuado")
    NATERA = (6, "grupo NATERA")
    SANE = (7, "voluntarios sanos")
    BASAL = (8, "extracció basal (antes de empezar cualquier tratamiento)")

    def __new__(cls, value, description):
        entry = object.__new__(cls)
        entry._value_ = value
        entry.description = description
        return entry

    def __repr__(self):
        return f"<{type(self).__name__}.{self.name}: ({self.value!r}, {self.description!r})>"
