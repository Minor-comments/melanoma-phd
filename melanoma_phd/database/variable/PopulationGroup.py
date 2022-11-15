from melanoma_phd.database.variable.CategoryEnum import CategoryEnum


class PopulationGroup(CategoryEnum):
    RC = (1, "RC con/sin BRAF/MEK")
    ANTI_PD1_CONT = (2, ">2 años antiPD1 ttm continuado")
    ANTI_PD1_STOP = (3, ">2a antiPD1 ttm STOP")
    PROGRESSION = (4, "Progresión")
    TTM_CONT = (5, ">6-12 meses ttm continuado")
    NATERA = (6, "grupo NATERA")
    SANE = (7, "voluntarios sanos")
    BASAL = (8, "extracció basal (antes de empezar cualquier tratamiento)")
