from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd
import yaml

from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.DatabaseSheet import DatabaseSheet
from melanoma_phd.database.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.variable.Variable import BaseVariable
from melanoma_phd.database.variable.VariableFatory import VariableFactory


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
        self.__load_database(database_file=database_file_path, config_file=config.database_config)

    def __load_database(self, database_file: str, config_file: str) -> None:
        with open(config_file, mode="rt", encoding="utf-8") as file_stream:
            yaml_dict = yaml.safe_load(file_stream)
        self._common_section_variable_name = yaml_dict["common_section_variable"]
        for section_config in yaml_dict["sections"]:
            section_name = next(iter(section_config))
            sheet = self.__load_database_sheet(
                database_file=database_file, config=section_config[section_name]
            )
            setattr(self.__class__, section_name, sheet)

    def __load_database_sheet(self, database_file: str, config: Dict[Any, Any]) -> DatabaseSheet:
        sheet_names = config["sheets"]
        dataframe = None
        for sheet_name in sheet_names:
            sheet_dataframe = pd.read_excel(io=database_file, sheet_name=sheet_name)
            if dataframe is not None:
                dataframe = dataframe.merge(
                    sheet_dataframe, on=self._common_section_variable_name, how="inner"
                )
            else:
                dataframe = sheet_dataframe

        variables_config = config["variables"]
        variables = None
        if variables_config:
            variables = self.__load_sheet_variables(variables_config)
        return DatabaseSheet(
            name=config["name"], dataframe=dataframe, variables_to_analyze=variables
        )

    def __load_sheet_variables(self, config: List[Dict[Any, Any]]) -> List[BaseVariable]:
        return [
            VariableFactory().create(**list(variable_config.values())[0])
            for variable_config in config
        ]
