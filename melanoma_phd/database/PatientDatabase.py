import os

import pandas as pd
from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.GoogleDriveService import GoogleDriveService


class PatientDatabase:
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"
    EXCEL_SHEET_NAMES = ["", "", "", "", "", ""]

    def __init__(self, config: AppConfig) -> None:
        database_file_path = os.path.join(
            config.data_folder, self.DATABASE_FOLDER, self.DATABASE_FILE
        )
        GoogleDriveService(config=config).download_excel_file_by_id(
            file_id=config.get_setting("database/file_id"), filename=database_file_path
        )
        self._file = database_file_path
        self.__load_database()

    @property
    def general_clinical_base(self) -> pd.DataFrame:
        return self._general_clinical_base

    @property
    def blood_parameters_base(self) -> pd.DataFrame:
        return self._blood_parameters_base

    @property
    def lf_dna_populations_base(self) -> pd.DataFrame:
        return self._lf_dna_populations_base

    @property
    def radiological_tests_base(self) -> pd.DataFrame:
        return self._radiological_tests_base

    @property
    def ap_ampliation_base(self) -> pd.DataFrame:
        return self._ap_ampliation_base

    def __load_database(self) -> None:
        self.__load_general_clinical_base()
        self.__load_blood_parameters_base()
        self.__load_lf_dna_populations_base()
        self.__load_radiological_tests_base()
        self.__load_ap_ampliation_base()

    def __load_general_clinical_base(self) -> None:
        self._general_clinical_base = pd.read_excel(
            io=self._file, sheet_name="BASE GENERAL CLÍNICA"
        )

    def __load_blood_parameters_base(self) -> None:
        self._blood_parameters_base = pd.read_excel(
            io=self._file, sheet_name="BASE PARAMETROS SANGRE"
        )

    def __load_lf_dna_populations_base(self) -> None:
        lf_dna_populations_base = pd.read_excel(
            io=self._file, sheet_name="BASE POBLACIONES LF-DNA (1-4)"
        )
        lf_dna_populations_base = lf_dna_populations_base.merge(
            right=pd.read_excel(io=self._file, sheet_name="BASE POBLACIONES LF-DNA (5-8)"),
            on="N. PACIENTE",
            how="inner",
        )
        lf_dna_populations_base = lf_dna_populations_base.merge(
            right=pd.read_excel(io=self._file, sheet_name="BASE POBLACIONES LF-DNA (9y10)"),
            on="N. PACIENTE",
            how="inner",
        )
        self._lf_dna_populations_base = lf_dna_populations_base

    def __load_radiological_tests_base(self) -> None:
        self._radiological_tests_base = pd.read_excel(
            io=self._file, sheet_name="BASE PRUEBAS RADIOLÓGICAS"
        )

    def __load_ap_ampliation_base(self) -> None:
        self._ap_ampliation_base = pd.read_excel(io=self._file, sheet_name="BASE AMPLIADA AP")
