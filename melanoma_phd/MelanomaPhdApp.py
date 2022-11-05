from __future__ import annotations

import logging

from melanoma_phd.config.AppConfig import AppConfig, create_config
from melanoma_phd.database.PatientDatabase import PatientDatabase
from melanoma_phd.logger.AppLogger import init_logger


def create_melanoma_phd_app(
    log_filename: str = "melanoma_phd.log",
    log_level: int = logging.DEBUG,
    data_folder: str = None,
) -> MelanomaPhdApp:
    init_logger(log_filename, log_level)
    config = create_config(data_folder)
    return MelanomaPhdApp(config)


class MelanomaPhdApp:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._data_base = PatientDatabase(config)
