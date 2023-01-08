from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
from packaging.version import Version
from packaging.version import parse as version_parse

from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.DatabaseSheet import DatabaseSheet
from melanoma_phd.database.source.DriveFileRepository import (
    DriveFileRepository,
    DriveFileRepositoryConfig,
    DriveVersionFileInfo,
)
from melanoma_phd.database.source.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.VariableFatory import VariableFactory


@dataclass
class IntegrityError:
    source_sheet: str
    target_sheet: str
    column: str


class PatientDatabase:
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"
    VERSION_REGEX = re.compile(r"versió\ +(?P<number>\d+)")

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._index_variable_name = None
        self._dataframe = None
        self._sheets = []
        self.__load()

    @property
    def file_info(self) -> DriveVersionFileInfo:
        return self._file_info

    @property
    def sheets(self) -> List[DatabaseSheet]:
        return self._sheets

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def variables(self) -> List[BaseVariable]:
        return [variable for sheet in self.sheets for variable in sheet.variables]

    def get_variable(self, variable_id: str) -> BaseVariable:
        for variable in self.variables:
            if variable.id == variable_id:
                return variable
        raise ValueError(f"'{variable_id}' variable identifier not found!")

    def reload(self) -> None:
        self.__load()

    def check_data_integrity(self) -> List[IntegrityError]:
        errors = []
        if not self.sheets:
            return errors
        first_sheet = self.sheets[0]
        for sheet in self.sheets[1:]:
            same_columns = first_sheet.dataframe.columns.intersection(sheet.dataframe.columns)
            for column in same_columns:
                if not first_sheet.dataframe[column].equals(sheet.dataframe[column]):
                    errors.append(
                        IntegrityError(
                            source_sheet=first_sheet.name, target_sheet=sheet.name, column=column
                        )
                    )

        return errors

    def __load(self) -> None:
        database_file_path = os.path.join(
            self._config.data_folder, self.DATABASE_FOLDER, self.DATABASE_FILE
        )
        database_file = self.__download_latest_version_file(
            google_service_account_info=self._config.google_service_account_info,
            drive_folder_id=self._config.get_setting("database/drive_folder_id"),
            database_file_path=database_file_path,
        )
        self.__load_database(database_file=database_file, config_file=self._config.database_config)

    def __download_latest_version_file(
        self,
        google_service_account_info: Dict[str, str],
        drive_folder_id: str,
        database_file_path: str,
    ) -> str:
        drive_version_info = self.__get_latest_version_file(
            google_service_account_info=google_service_account_info, drive_folder_id=drive_folder_id
        )
        if drive_version_info is None:
            raise RuntimeError("Latest database version file not found in Goolge Drive!")

        self._file_info = drive_version_info
        database_file = self.__create_database_filename(
            file_path=database_file_path, version=drive_version_info.version
        )
        self.__download_database_file(
            google_service_account_info=google_service_account_info,
            drive_file_id=drive_version_info.id,
            database_file=database_file,
        )
        self._file_info = drive_version_info
        return database_file

    def __get_latest_version_file(
        self, google_service_account_info: Dict[str, str], drive_folder_id: str
    ) -> DriveVersionFileInfo:
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
            logging.debug(
                f"Skipping '{file_name}' as database version since has no defined version"
            )
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
        self._index_variable_name = yaml_dict["index_variable"]
        for section_config in yaml_dict["sections"]:
            section_name = next(iter(section_config))
            sheet = self.__load_database_sheet(
                database_file=database_file, config=section_config[section_name]
            )
            setattr(self.__class__, section_name, sheet)
            self._sheets.append(sheet)
            if self._dataframe is None:
                self._dataframe = sheet.dataframe
            else:
                self._dataframe = self._dataframe.merge(
                    sheet.dataframe, how="inner", validate="1:1"
                )

    def __load_database_sheet(self, database_file: str, config: Dict[Any, Any]) -> DatabaseSheet:
        sheet_names = config["sheets"]
        dataframe = None
        for sheet_name in sheet_names:
            sheet_dataframe = pd.read_excel(io=database_file, sheet_name=sheet_name)
            if dataframe is not None:
                dataframe = dataframe.merge(sheet_dataframe, how="inner")
            else:
                dataframe = sheet_dataframe

        dataframe = dataframe[dataframe[self._index_variable_name].notna()]
        variables_config = config["variables"]
        variables = self.__load_sheet_variables(dataframe, variables_config)

        variables_config = config.get("dynamic_variables")
        if variables_config:
            dynamic_variables, dataframe = self.__load_sheet_dynamic_variables(
                config=variables_config, dataframe=dataframe
            )
            variables.extend(dynamic_variables)
        return DatabaseSheet(name=config["name"], dataframe=dataframe, variables=variables)

    def __load_sheet_variables(
        self, dataframe: pd.DataFrame, config: List[Dict[Any, Any]]
    ) -> List[BaseVariable]:
        variables = {}
        if config:
            for variable in [
                VariableFactory().create(dataframe=dataframe, **list(variable_config.values())[0])
                for variable_config in config
            ]:
                variables[variable.id] = variable

        for column in dataframe:
            if column not in variables.keys():
                variable = VariableFactory().create_from_series(dataframe=dataframe, id=column)
                if variable:
                    variables[variable.id] = variable
        return list(variables.values())

    def __load_sheet_dynamic_variables(
        self, config: List[Dict[Any, Any]], dataframe: pd.DataFrame
    ) -> Tuple[List[BaseVariable], pd.DataFrame]:
        new_variables = []
        for variable_config in config:
            new_variable, dataframe = VariableFactory().create_dynamic(
                dataframe=dataframe, **list(variable_config.values())[0]
            )
            new_variables.append(new_variable)
        return [new_variables, dataframe]
