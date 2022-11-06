from __future__ import annotations

import logging
import os

from melanoma_phd.config.AppConfig import AppConfig, create_config
from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.logger.AppLogger import init_logger


def create_melanoma_phd_app(
    log_filename: str = "melanoma_phd.log",
    log_level: int = logging.DEBUG,
    data_folder: str = None,
) -> MelanomaPhdApp:
    config = create_config(data_folder)
    log_filename = os.path.join(config.log_folder, log_filename)
    init_logger(log_filename, log_level)
    return MelanomaPhdApp(config)


class MelanomaPhdApp:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._database = PatientDatabase(config)

    @property
    def database(self) -> PatientDatabase:
        return self._database
