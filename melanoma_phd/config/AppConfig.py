import json
import os
from typing import Dict

from melanoma_phd import __version__
from melanoma_phd.config.JsonConfig import JsonConfig


class AppConfig(JsonConfig):
    def __init__(self, config_file: str, data_folder: str) -> None:
        super().__init__(config_file)
        self._name = self.get_setting("config/name")
        self._data_folder = os.path.join(data_folder, self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_folder(self) -> str:
        return self._data_folder

    @property
    def log_folder(self) -> str:
        return os.path.join(self.data_folder, "log")

    @property
    def version(self) -> str:
        return __version__

    @property
    def google_service_account_info(self) -> Dict:
        project_id = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PROJECT_ID", None)
        if project_id:
            return {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": os.environ["GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID"],
                "private_key": os.environ["GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY"],
                "client_email": os.environ["GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL"],
                "client_id": os.environ["GOOGLE_SERVICE_ACCOUNT_CLIENT_ID"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/melanoma-phd-client%40melanoma-phd.iam.gserviceaccount.com",
            }
        else:
            folder_name = os.path.dirname(os.path.abspath(__file__))
            service_account_file = os.path.join(folder_name, "service_account_file.json")
            if os.path.exists(service_account_file):
                with open(service_account_file) as fd:
                    return json.loads(fd.read())
            else:
                raise RuntimeError(
                    "Google service account info has not been provided either by 'GOOGLE_SERVICE_ACCOUNT_INFO' environment variable or 'service_account_file.json' file."
                )


def create_config(data_folder=None) -> AppConfig:
    """
    Creates the configuration object for the application.
    """
    folder_name = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(folder_name, "config.json")
    if not data_folder:
        data_folder = os.path.join(folder_name, "../../", "data")
    config = AppConfig(config_file, data_folder)
    print(f"'{config.name}' environment has been configured successfully", flush=True)
    return config
