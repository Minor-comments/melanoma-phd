from __future__ import annotations

import logging
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
from packaging.version import Version
from packaging.version import parse as version_parse

from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.config.IterationConfigGenerator import IterationConfigGenerator
from melanoma_phd.database.AbstractPatientDatabaseView import AbstractPatientDatabaseView
from melanoma_phd.database.DatabaseSheet import DatabaseSheet
from melanoma_phd.database.filter.BaseFilter import BaseFilter
from melanoma_phd.database.filter.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.database.PatientDatabaseView import PatientDatabaseView
from melanoma_phd.database.source.DriveFileRepository import (
    DriveFileRepository,
    DriveFileRepositoryConfig,
    DriveVersionFileInfo,
)
from melanoma_phd.database.source.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.IterationCategoricalVariable import IterationCategoricalVariable
from melanoma_phd.database.variable.IterationScalarVariable import IterationScalarVariable
from melanoma_phd.database.variable.ReferenceIterationVariable import ReferenceIterationVariable
from melanoma_phd.database.variable.VariableFactory import VariableFactory


class IntegrityError(Exception):
    def __init__(self, source_sheet: str, target_sheet: str, columns: List[str]) -> None:
        self.source_sheet: str = source_sheet
        self.target_sheet: str = target_sheet
        self.columns: List[str] = columns
        super().__init__(
            f"Source sheet '{source_sheet}' has different column data {columns} in comparison to target sheet '{target_sheet}'!"
        )


class PatientDatabase(AbstractPatientDatabaseView):
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"
    VERSION_REGEX = re.compile(r"versió\ +(?P<number>\d+)")

    def __init__(self, config: AppConfig) -> None:
        self._config: AppConfig = config
        self._index_variable_name: Optional[str] = None
        self._dataframe: Optional[pd.DataFrame] = None
        self._sheets: List[DatabaseSheet] = []
        self.__load()

    @property
    def file_info(self) -> DriveVersionFileInfo:
        return self._file_info

    @property
    def sheets(self) -> List[DatabaseSheet]:
        return self._sheets

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._dataframe is None:
            raise ValueError(
                f"Database has not been loaded. Please review code to ensure the process is working as expected"
            )
        return self._dataframe

    @property
    def variables(self) -> List[BaseVariable]:
        return [variable for sheet in self.sheets for variable in sheet.variables]

    def get_iteration_variables_of(
        self, reference_variable: ReferenceIterationVariable
    ) -> List[BaseVariable]:
        iteration_variables = self.get_variables_by_type(
            [IterationScalarVariable, IterationCategoricalVariable]
        )
        return [
            variable
            for variable in iteration_variables
            if variable.reference_variable == reference_variable
        ]

    def reload(self) -> None:
        self.__load()

    def filter(self, filters: List[BaseFilter], name: Optional[str] = None) -> PatientDatabaseView:
        dataframe_to_filter = self.dataframe.copy()
        df_result = PatientDataFilterer().filter(dataframe_to_filter, filters)
        if name:
            df_result.name = name
        variables = [deepcopy(variable) for variable in self.variables]
        return PatientDatabaseView(dataframe=df_result, variables=variables)

    def __check_equal_column_data(
        self, left_dataframe: pd.DataFrame, right_dataframe: pd.DataFrame
    ) -> List[str]:
        not_equal_columns: List[str] = []
        same_columns = left_dataframe.columns.intersection(right_dataframe.columns)
        for column in same_columns:
            if not left_dataframe[column].equals(right_dataframe[column]):
                not_equal_columns.append(column)

        return not_equal_columns

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
    ) -> Optional[DriveVersionFileInfo]:
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
        path = Path(file_path)
        database_file = str(
            Path(
                path.parent,
                f"{path.stem}_{str(version)}{path.suffix}",
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
                not_equal_columns = self.__check_equal_column_data(
                    left_dataframe=self._dataframe, right_dataframe=sheet.dataframe
                )
                if not_equal_columns:
                    raise IntegrityError(
                        source_sheet=sheet.name,
                        target_sheet="top dataframe",
                        columns=not_equal_columns,
                    )
                self._dataframe = self._dataframe.merge(
                    sheet.dataframe,
                    how="inner",
                    validate="1:1",
                )
        self._dataframe.set_index(self._index_variable_name, inplace=True)

    def __load_database_sheet(self, database_file: str, config: Dict[Any, Any]) -> DatabaseSheet:
        database_sheet_name = config["name"]
        sheet_names = config["sheets"]
        dataframe = None
        for sheet_name in sheet_names:
            sheet_dataframe: pd.DataFrame = pd.read_excel(io=database_file, sheet_name=sheet_name)
            if dataframe is not None:
                not_equal_columns = self.__check_equal_column_data(
                    left_dataframe=dataframe, right_dataframe=sheet_dataframe
                )
                if not_equal_columns:
                    raise IntegrityError(
                        source_sheet=sheet_name,
                        target_sheet=database_sheet_name,
                        columns=not_equal_columns,
                    )
                dataframe = dataframe.merge(sheet_dataframe, how="inner")
            else:
                dataframe = sheet_dataframe

        if dataframe is None:
            raise ValueError("Sheets not found in config file")
        if self._index_variable_name is None:
            raise ValueError("Index variable name not found in config")

        dataframe = dataframe.loc[dataframe[self._index_variable_name].notna()]
        dataframe.name = database_sheet_name
        variables_config = config["variables"]
        variables = self.__load_sheet_variables(dataframe, variables_config)

        variables_config = config.get("dynamic_variables")
        if variables_config:
            dynamic_variables, dataframe = self.__load_sheet_dynamic_variables(
                config=variables_config, dataframe=dataframe
            )
            variables.extend(dynamic_variables)
        return DatabaseSheet(name=database_sheet_name, dataframe=dataframe, variables=variables)

    def __load_sheet_variables(
        self, dataframe: pd.DataFrame, config: List[Dict[Any, Any]]
    ) -> List[BaseVariable]:
        config_variables = {}
        if config:
            config_variables = self.__create_variables_from_config(
                dataframe=dataframe, config=config
            )
        variables: List[BaseVariable] = list(config_variables.values())
        missing_columns = [
            str(column) for column in dataframe if column not in config_variables.keys()
        ]
        for column in missing_columns:
            new_variable = VariableFactory().create_from_series(dataframe=dataframe, id=column)
            if new_variable:
                variables.append(new_variable)
        return variables

    def __create_variables_from_config(
        self, dataframe: pd.DataFrame, config: List[Dict[Any, Any]]
    ) -> Dict[str, BaseVariable]:
        created_variables: Dict[str, BaseVariable] = {}
        errors: List[str] = []
        for variable_config in config:
            if IterationConfigGenerator.is_iteration(variable_config):
                try:
                    iterated_variable_configs = IterationConfigGenerator.generate_iterated(
                        variable_config
                    )
                    iterated_variables = []
                    for variable in [
                        VariableFactory().create(
                            dataframe=dataframe, **list(variable_config.values())[0]
                        )
                        for variable_config in iterated_variable_configs
                    ]:
                        created_variables[variable.id] = variable
                        iterated_variables.append(variable)
                    (
                        iteration_variable_config,
                        reference_variable_id,
                    ) = IterationConfigGenerator.generate_iteration(variable_config)
                    if reference_variable_id:
                        reference_variable = created_variables[reference_variable_id]
                        iteration_variable, dataframe = VariableFactory().create_iteration(
                            dataframe=dataframe,
                            reference_variable=reference_variable,
                            iterated_variables=iterated_variables,
                            **list(iteration_variable_config.values())[0],
                        )
                        created_variables[iteration_variable.id] = iteration_variable
                    else:
                        (
                            reference_variable,
                            dataframe,
                        ) = VariableFactory().create_reference_iteration(
                            dataframe=dataframe,
                            iterated_variables=iterated_variables,
                            **list(iteration_variable_config.values())[0],
                        )
                        created_variables[reference_variable.id] = reference_variable
                except KeyError as error:
                    raise ValueError(
                        f"Database loading error: '{error}'. The next config variables could not been loaded causing the database loading abortation:\n - "
                        + "\n - ".join([str(error) for error in errors])
                    )
                except ValueError as error:
                    errors.append(
                        f"Error creating iteration variable '{variable_config}': {str(error)}"
                    )
            else:
                try:
                    variable = VariableFactory().create(
                        dataframe=dataframe, **list(variable_config.values())[0]
                    )
                    created_variables[variable.id] = variable
                except ValueError as error:
                    errors.append(f"Error creating variable '{variable_config}': {str(error)}")
        if errors:
            raise ValueError(
                f"Database configuration error. The next config variables could not been loaded:\n - "
                + "\n - ".join([str(error) for error in errors])
            )
        return created_variables

    def __load_sheet_dynamic_variables(
        self, config: List[Dict[Any, Any]], dataframe: pd.DataFrame
    ) -> Tuple[List[BaseVariable], pd.DataFrame]:
        new_variables: List[BaseVariable] = []
        for variable_config in config:
            new_variable, dataframe = VariableFactory().create_dynamic(
                dataframe=dataframe, **list(variable_config.values())[0]
            )
            new_variables.append(new_variable)
        return (new_variables, dataframe)
