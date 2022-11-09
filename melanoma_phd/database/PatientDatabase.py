import os

import pandas as pd

from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.DatabaseSheet import DatabaseSheet
from melanoma_phd.database.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.Variable import CategoricalVariable


class PatientDatabase:
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"

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
    def general_clinical_database(self) -> DatabaseSheet:
        return self._general_clinical_base

    @property
    def blood_parameters_database(self) -> DatabaseSheet:
        return self._blood_parameters_base

    @property
    def lf_dna_populations_database(self) -> DatabaseSheet:
        return self._lf_dna_populations_base

    @property
    def radiological_tests_database(self) -> DatabaseSheet:
        return self._radiological_tests_base

    @property
    def ap_ampliation_database(self) -> DatabaseSheet:
        return self._ap_ampliation_base

    def __load_database(self) -> None:
        self.__load_general_clinical_base()
        self.__load_blood_parameters_base()
        self.__load_lf_dna_populations_base()
        self.__load_radiological_tests_base()
        self.__load_ap_ampliation_base()

    def __load_general_clinical_base(self) -> None:
        sheet_name = "BASE GENERAL CLÍNICA"
        dataframe = pd.read_excel(io=self._file, sheet_name=sheet_name)
        variables = [CategoricalVariable(name="SEXO", category_names={0.0: "Hombre", 1.0: "Mujer"})]
        self._general_clinical_base = DatabaseSheet(
            name=sheet_name, dataframe=dataframe, variables_to_analyze=variables
        )

    def __load_blood_parameters_base(self) -> None:
        sheet_name = "BASE PARAMETROS SANGRE"
        dataframe = pd.read_excel(io=self._file, sheet_name=sheet_name)
        self._blood_parameters_base = DatabaseSheet(
            name=sheet_name, dataframe=dataframe, variables_to_analyze=[]
        )

    def __load_lf_dna_populations_base(self) -> None:
        dataframe = pd.read_excel(io=self._file, sheet_name="BASE POBLACIONES LF-DNA (1-4)")
        dataframe = dataframe.merge(
            right=pd.read_excel(io=self._file, sheet_name="BASE POBLACIONES LF-DNA (5-8)"),
            on="N. PACIENTE",
            how="inner",
        )
        dataframe = dataframe.merge(
            right=pd.read_excel(io=self._file, sheet_name="BASE POBLACIONES LF-DNA (9y10)"),
            on="N. PACIENTE",
            how="inner",
        )
        sheet_name = "BASE POBLACIONES LF-DNA"
        self._lf_dna_populations_base = DatabaseSheet(
            name=sheet_name, dataframe=dataframe, variables_to_analyze=[]
        )

    def __load_radiological_tests_base(self) -> None:
        sheet_name = "BASE PRUEBAS RADIOLÓGICAS"
        dataframe = pd.read_excel(io=self._file, sheet_name=sheet_name)
        self._radiological_tests_base = DatabaseSheet(
            name=sheet_name, dataframe=dataframe, variables_to_analyze=[]
        )

    def __load_ap_ampliation_base(self) -> None:
        sheet_name = "BASE AMPLIADA AP"
        dataframe = pd.read_excel(io=self._file, sheet_name=sheet_name)
        self._ap_ampliation_base = DatabaseSheet(
            name=sheet_name, dataframe=dataframe, variables_to_analyze=[]
        )
