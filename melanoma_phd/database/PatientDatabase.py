import os

import pandas as pd
from melanoma_phd.config.AppConfig import AppConfig
from melanoma_phd.database.ExcelDownloader import ExcelDownloader


class PatientDatabase:
    DATABASE_FOLDER = "database"
    DATABASE_FILE = "patient_database.xlsx"

    def __init__(self, config: AppConfig) -> None:
        database_file_path = os.path.join(
            config.data_folder, self.DATABASE_FOLDER, self.DATABASE_FILE
        )
        ExcelDownloader().download(
            document_id=config.get_setting("database/file_id"), filename=database_file_path
        )
        self._file = database_file_path
        self.__load_database()

    def __load_database(self) -> None:
        pd.read_excel(self._file)
