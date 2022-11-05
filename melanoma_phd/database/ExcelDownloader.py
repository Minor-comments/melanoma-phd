import logging
import os
import shutil

from melanoma_phd.database.GoogleDriveService import GoogleDriveService
from melanoma_phd.database.TimestampSaver import TimestampSaver


class ExcelDownloader:
    """
    Download Excel files using Gooogle Drive service.
    """

    TIMESTAMP_FILENAME = ".timestamp"

    def __init__(self) -> None:
        self._service = GoogleDriveService()

    def download(self, document_id: str, filename: str):
        folder = os.path.dirname(filename)
        timestamp_file = os.path.join(folder, self.TIMESTAMP_FILENAME)
        download = True
        modified_date = self._service.get_modified_date_file_by_id(file_id=document_id)
        if os.path.exists(filename):
            if os.path.exists(timestamp_file):
                download_date = TimestampSaver.load_date(timestamp_file)
                download = download_date < modified_date
            else:
                logging.warning(f"'{filename}' file has no timestamp file!")

        if download:
            logging.info(f"Downloading '{filename}' csv file...")
            os.makedirs(folder, exist_ok=True)
            file_tmp_name = filename + "_tmp"
            with open(file_tmp_name, "wb") as file_tmp:
                self._service.download_excel_file_by_id(document_id, file_tmp)
            shutil.copyfile(file_tmp_name, filename)
            os.remove(file_tmp_name)
            TimestampSaver.save_date(timestamp_file, modified_date)
