import io
import logging
import os.path
import pickle
import tempfile
from datetime import datetime
from typing import Union

from google.api_core import retry
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def retry_error_log(error: Exception):
    logging.error(f"Google Drive service error: {error}. Retrying operation...")


class GoogleDriveService:
    """
    Google Drive service helper
    """

    DATA_FOLDER = os.path.join(tempfile.gettempdir(), "data")

    def __init__(self) -> None:
        self._credentials = self.__load_credentials()
        self._service = build("drive", "v3", credentials=self._credentials)

    @retry.Retry(predicate=retry.if_exception_type(HttpError), on_error=retry_error_log)
    def get_modified_date_file_by_id(self, file_id: str) -> datetime:
        result = self._service.files().get(fileId=file_id, fields="modifiedTime").execute()
        return datetime.strptime(result["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

    @retry.Retry(predicate=retry.if_exception_type(HttpError), on_error=retry_error_log)
    def download_excel_file_by_id(
        self, file_id: str, local_fd: Union[io.TextIOWrapper, io.BytesIO]
    ) -> None:
        """Download a Drive file's by ID to the local filesystem.
        Args:
            file_id: ID of the Drive file that will downloaded.
            local_fd: io.Base or file object, the stream that the Drive file's
            contents will be written to.
        """
        request = self._service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        media_request = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = media_request.next_chunk()
        local_fd.write(fh.getvalue())

    def __load_credentials(self) -> Credentials:
        logging.debug(f"Loading Google Drive credentials")
        script_path = os.path.dirname(os.path.abspath(__file__))
        token_pickle_file = os.path.join(script_path, "token.pickle")
        credentials = self.__load_token_pickle(token_pickle_file)
        if not self.__check_credentials(credentials):
            token_pickle_file = os.path.join(self.DATA_FOLDER, "token.pickle")
            tmp_credentials = self.__load_token_pickle(token_pickle_file)
            if self.__check_credentials(tmp_credentials):
                credentials = tmp_credentials
            else:
                credentials = credentials or tmp_credentials

        if not self.__check_credentials(credentials):
            credentials_file = os.path.join(script_path, "credentials.json")
            credentials = self.__load_credentials_from_files(credentials, credentials_file)

            try:
                token_pickle_file = os.path.join(script_path, "token.pickle")
                self.__save_credentials(credentials, token_pickle_file)
            except OSError:
                token_pickle_file = os.path.join(self.DATA_FOLDER, "token.pickle")
                try:
                    self.__save_credentials(credentials, token_pickle_file)
                except OSError as error:
                    logging.warning(
                        f"Error when saving credentials. Next run will require credentials again. Error: {error}"
                    )
        return credentials

    def __check_credentials(self, credentials: Credentials) -> bool:
        logging.debug(f"Checking Google Drive credentials: {credentials}")
        if credentials is not None:
            logging.debug(f"\t{credentials.valid} ({credentials.expired} - {credentials.expiry})")
        return credentials and credentials.valid

    def __load_token_pickle(self, token_pickle_file: str) -> Credentials:
        logging.debug(f"Loading Google Drive token from '{token_pickle_file}'")
        credentials = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_pickle_file):
            with open(token_pickle_file, "rb") as token:
                credentials = pickle.load(token)
        return credentials

    def __load_credentials_from_files(
        self, credentials: Credentials, credentials_file: str
    ) -> Credentials:
        logging.debug(f"Loading Google Drive credentials from '{credentials_file}'")
        if credentials and credentials.expired and credentials.refresh_token:
            logging.debug("Refreshing Google Drive credentials")
            credentials.refresh(Request())
        else:
            logging.debug("Loading Google Drive credentials from files")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            credentials = flow.run_local_server(port=0)
        return credentials

    def __save_credentials(self, credentials, token_pickle_file):
        logging.debug(f"Saving Google Drive token to '{token_pickle_file}'")
        # Save the credentials for the next run
        with open(token_pickle_file, "wb") as token:
            pickle.dump(credentials, token)
