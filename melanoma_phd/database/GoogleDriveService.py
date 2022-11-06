import io
import logging
import os
import shutil
import tempfile
from datetime import datetime

from google.api_core import retry
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from melanoma_phd.database.TimestampSaver import TimestampSaver

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def retry_error_log(error: Exception):
    logging.error(f"Google Drive service error: {error}. Retrying operation...")


class GoogleDriveService:
    """
    Google Drive service helper.
    """

    DATA_FOLDER = os.path.join(tempfile.gettempdir(), "data")
    TIMESTAMP_FILENAME = ".timestamp"

    def __init__(self) -> None:
        self._credentials = self.__load_credentials()
        self._service = build("drive", "v3", credentials=self._credentials)

    @retry.Retry(predicate=retry.if_exception_type(HttpError), on_error=retry_error_log)
    def get_modified_date_file_by_id(self, file_id: str) -> datetime:
        result = self._service.files().get(fileId=file_id, fields="modifiedTime").execute()
        return datetime.strptime(result["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

    @retry.Retry(predicate=retry.if_exception_type(HttpError), on_error=retry_error_log)
    def download_excel_file_by_id(self, file_id: str, filename: str, force=False) -> None:
        """Download a Drive file's by ID to the local filesystem.
        Args:
            file_id: ID of the Drive file that will downloaded.
            filename: path to the file to create on local with downloaded file contents.
            force: True for skipping the downloading action when file on Drive has no changes.
        """
        folder = os.path.dirname(filename)
        timestamp_file = os.path.join(folder, self.TIMESTAMP_FILENAME)
        download = True
        if os.path.exists(filename) and not force:
            if os.path.exists(timestamp_file):
                download_date = TimestampSaver.load_date(timestamp_file)
                modified_date = self.get_modified_date_file_by_id(file_id=file_id)
                download = download_date < modified_date
            else:
                logging.warning(f"'{filename}' file has no timestamp file!")

        if download:
            self.__download_file(file_id, filename)
            TimestampSaver.save_date(timestamp_file, modified_date)
        else:
            logging.debug(f"Downloading skipped since '{filename}' file is up-to-date.")

    def __load_credentials(self) -> Credentials:
        logging.debug(f"Loading Google Drive credentials")
        script_path = os.path.dirname(os.path.abspath(__file__))
        credentials_file = os.path.join(script_path, "service_account_file.json")
        credentials = service_account.Credentials.from_service_account_file(
            filename=credentials_file, scopes=SCOPES
        )
        return credentials

    def __download_file(self, file_id: str, filename: str) -> None:
        logging.info(f"Downloading '{filename}' file...")
        folder = os.path.dirname(filename)
        os.makedirs(folder, exist_ok=True)
        file_tmp_name = filename + "_tmp"
        with open(file_tmp_name, "wb") as file_tmp:
            request = self._service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            media_request = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                _, done = media_request.next_chunk()
            file_tmp.write(fh.getvalue())
        shutil.copyfile(file_tmp_name, filename)
        os.remove(file_tmp_name)
