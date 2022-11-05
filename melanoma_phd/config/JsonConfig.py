import json
import os


class JsonConfig:
    """Load a json file which store the application configuration.
    Features:
    - Entries can be retrieved by key path inside the file like 'bubble/web_url_id'.
    - Entries pointing to file system path that are named using 'file_path' word in the key name are resolved with absolute path.
        Example: '"authorization_json_file_path": "cloud_function_auth.json"' is resolved to '~/home/documents/user/malanoma-phd/melanoma_phd/config/cloud_function_auth.json'.
    """

    def __init__(self, config_file):
        self._file = config_file
        with open(config_file) as json_file:
            self._json = json.load(json_file)
        self.__resolve_paths(self._json)

    def get_setting(self, entry):
        """
        Get configuration values by entry. The entry could be a simple name or a path separated by '/', like 'bubble/web_url_id'.
        """
        keys = entry.split("/")
        node = self._json
        try:
            for key in keys[:-1]:
                node = node[key]
            return node[keys[-1]]
        except KeyError:
            raise ValueError(f"'{entry}' setting entry not found in '{self._file}' file!")

    def __resolve_paths(self, dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                self.__resolve_paths(value)
            else:
                if "file_path" in key:
                    file_path = os.path.abspath(os.path.join(os.path.dirname(self._file), value))
                    if not os.path.exists(file_path):
                        raise ValueError(
                            f"'{value}' system path defined as '{key}' configuration entry not found",
                        )
                    dictionary[key] = file_path
