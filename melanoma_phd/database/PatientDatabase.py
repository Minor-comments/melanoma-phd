from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml
from packaging.version import Version
from packaging.version import parse as version_parse

from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.DatabaseSheet import DatabaseSheet
from melanoma_phd.database.source.DriveFileRepository import (
    DriveFileRepository,
    DriveFileRepositoryConfig,
    DriveVersionFile,
)
from melanoma_phd.database.source.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.VariableFatory import VariableFactory


class PatientDatabase:
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"
    VERSION_REGEX = re.compile(r"versió\ +(?P<number>\d+)")

    def __init__(self, config: AppConfig) -> None:
        database_file_path = os.path.join(
            config.data_folder, self.DATABASE_FOLDER, self.DATABASE_FILE
        )
        database_file = self.__download_latest_version_file(
            google_service_account_info=config.google_service_account_info,
            drive_folder_id=config.get_setting("database/drive_folder_id"),
            database_file_path=database_file_path,
        )
        self.__load_database(database_file=database_file, config_file=config.database_config)

    def __download_latest_version_file(
        self,
        google_service_account_info: Dict[str, str],
        drive_folder_id: str,
        database_file_path: str,
    ) -> str:
        latest_version = self.__get_latest_version_file(
            google_service_account_info=google_service_account_info, drive_folder_id=drive_folder_id
        )
        if latest_version is None:
            raise RuntimeError("Latest database version file not found in Goolge Drive!")

        database_file = self.__create_database_filename(
            file_path=database_file_path, version=latest_version.version
        )
        self.__download_database_file(
            google_service_account_info=google_service_account_info,
            drive_file_id=latest_version.id,
            database_file=database_file,
        )
        return database_file

    def __get_latest_version_file(
        self, google_service_account_info: Dict[str, str], drive_folder_id: str
    ) -> DriveVersionFile:
        config = DriveFileRepositoryConfig(
            google_service_account_info=google_service_account_info,
            drive_folder_id=drive_folder_id,
            filter=lambda file_name: PatientDatabase.filter_database_file_version(
                file_name=file_name
            ),
        )
        return DriveFileRepository(config).get_latest_file_version()

    @classmethod
    def filter_database_file_version(cls, file_name: str) -> Optional[Version]:
        match = cls.VERSION_REGEX.search(file_name)
        if match:
            return version_parse(match.group("number"))
        else:
            return None

    def __download_database_file(
        self,
        google_service_account_info: Dict[str, str],
        drive_file_id: str,
        database_file: str,
    ) -> None:
        GoogleDriveService(
            google_service_account_info=google_service_account_info
        ).download_excel_file_by_id(file_id=drive_file_id, filename=database_file)

    def __create_database_filename(self, file_path: str, version: Version) -> str:
        file_path = Path(file_path)
        database_file = str(
            Path(
                file_path.parent,
                f"{file_path.stem}_{str(version)}{file_path.suffix}",
            )
        )
        return database_file

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

        variables_config = config.get("dynamic_variables")
        if variables_config:
            variables.extend(
                self.__load_sheet_dynamic_variables(config=variables_config, dataframe=dataframe)
            )
        return DatabaseSheet(
            name=config["name"], dataframe=dataframe, variables_to_analyze=variables
        )

    def __load_sheet_variables(self, config: List[Dict[Any, Any]]) -> List[BaseVariable]:
        return [
            VariableFactory().create(**list(variable_config.values())[0])
            for variable_config in config
        ]

    def __load_sheet_dynamic_variables(
        self, config: List[Dict[Any, Any]], dataframe: pd.DataFrame
    ) -> List[BaseVariable]:
        new_variables = []
        for variable_config in config:
            new_variable = VariableFactory().create_dynamic(**list(variable_config.values())[0])
            dataframe = new_variable.add_variable_to_dataframe(dataframe)
            new_variables.append(new_variable)
        return new_variables
