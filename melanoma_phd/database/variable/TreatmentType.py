from melanoma_phd.database.variable.CategoryEnum import CategoryEnum


class TreatmentType(CategoryEnum):
    NO = (0, "NO")
    BRAF_MEK = (1, "BRAF+MEK")
    ANTI_PD1_BASED = (2, "anti-PD1 based")
    ANTI_PD1_MONTHERAPY = (3, "anti-PD1 monotherapy")
    TRIPLETE = (4, "Triplete")
    ANTI_PD1_ANTI_CTLA4 = (5, "antiPD1+antiCTLA4")
    ANTI_CTLA4_BASED = (6, "antiCTLA4 based")
    OTHER = (7, "Other")
    ANTI_PDL1_BASED = (8, "Anti-PDL1 based")
