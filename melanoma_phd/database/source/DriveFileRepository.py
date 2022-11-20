from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List

from packaging.version import Version

from melanoma_phd.database.source.GoogleDriveService import DriveFileInfo, GoogleDriveService


@dataclass
class DriveVersionFileInfo:
    id: str
    name: str
    modified_date: datetime
    version: Version

    def __str__(self) -> str:
        return (
            f"version: {self.version}"
            f"\nfilename: {self.name}"
            f"\nmodified_date: {self.modified_date}"
            f"\nid: {self.id}"
        )

    @classmethod
    def from_drive_file(cls, drive_file: DriveFileInfo, version: Version) -> DriveVersionFileInfo:
        return cls(
            id=drive_file.id,
            name=drive_file.name,
            modified_date=drive_file.modified_date,
            version=version,
        )


@dataclass
class DriveFileRepositoryConfig:
    google_service_account_info: Dict[str, str]
    drive_folder_id: str
    """Filter if a file inside Drive repository folder is considered a file version or not by its file name.
    It should Return the version of the file or None if the file is not included as file version set.
    """
    filter: Callable[[str], Version]


class DriveFileRepository:
    def __init__(self, config: DriveFileRepositoryConfig) -> None:
        self._config = config

    def get_file_versions(self) -> List[DriveVersionFileInfo]:
        drive_service = GoogleDriveService(
            google_service_account_info=self._config.google_service_account_info
        )
        files = drive_service.list_files(folder_id=self._config.drive_folder_id)
        file_versions = []
        for file in files:
            version = self._config.filter(file.name)
            if version:
                file_versions.append(DriveVersionFileInfo.from_drive_file(file, version=version))

        return file_versions

    def get_latest_file_version(self) -> DriveVersionFileInfo:
        latest_file_version = None
        drive_files = self.get_file_versions()
        for drive_file in drive_files:
            if latest_file_version is None or drive_file.version > latest_file_version.version:
                latest_file_version = drive_file
        return latest_file_version
