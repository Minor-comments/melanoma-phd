import re
from copy import deepcopy
from typing import Any, Dict, List, Tuple


class IterationConfigGenerator:
    ITERATION_REGEX = "(\d+)\.\.(\d+)"
    ITERATION_INDEX_REGEX = "\{N\}"
    ITERATED_PROPERTY_PREFIX = "_iterated_"
    ITERATION_PROPERTY_PREFIX = "_iteration_"
    ITERATION_PROPERTY_REFERENCE_VARIABLE = "reference_variable_id"

    def __init__(self) -> None:
        pass

    @classmethod
    def is_iteration(cls, config: Dict[str, Any]) -> bool:
        root_key = next(iter(config))
        return re.search(pattern=cls.ITERATION_REGEX, string=root_key) != None

    @classmethod
    def generate_iterated(cls, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        root_key = next(iter(config))
        result = re.search(pattern=cls.ITERATION_REGEX, string=root_key)
        if result:
            new_config = deepcopy(config)
            cls.remove_dict_keys(new_config, cls.ITERATION_PROPERTY_PREFIX)
            cls.remove_dict_prefix(new_config, cls.ITERATED_PROPERTY_PREFIX)
            start_index = int(result.group(1))
            end_index = int(result.group(2))
            configs: List[Dict[str, Any]] = []
            for i in range(start_index, end_index + 1):
                configs.append(cls.__generate_iterated_config(config=new_config, index=i))
            return configs
        else:
            return [config]

    @classmethod
    def generate_iteration(cls, config: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        root_key = next(iter(config))
        result = re.search(pattern=cls.ITERATION_REGEX, string=root_key)
        if result:
            new_config = deepcopy(config)
            cls.remove_dict_keys(new_config, cls.ITERATED_PROPERTY_PREFIX)
            cls.remove_dict_prefix(new_config, cls.ITERATION_PROPERTY_PREFIX)
            reference_variable_id = cls.pop_dict_property(
                new_config, cls.ITERATION_PROPERTY_REFERENCE_VARIABLE
            )
            return (new_config, reference_variable_id)
        else:
            return (config, "")

    @staticmethod
    def remove_dict_keys(dictionary: Dict[str, Any], prefix: str) -> None:
        keys_to_remove = [
            key for key in dictionary.keys() if isinstance(key, str) and key.startswith(prefix)
        ]
        for key in keys_to_remove:
            dictionary.pop(key)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                IterationConfigGenerator.remove_dict_keys(value, prefix)

    @staticmethod
    def remove_dict_prefix(dictionary: Dict[str, Any], prefix: str) -> None:
        keys_to_change = [
            key for key in dictionary.keys() if isinstance(key, str) and key.startswith(prefix)
        ]
        for key in keys_to_change:
            dictionary[key.removeprefix(prefix)] = dictionary.pop(key)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                IterationConfigGenerator.remove_dict_prefix(value, prefix)

    @staticmethod
    def pop_dict_property(dictionary: Dict[str, Any], key: str) -> Any:
        if key in dictionary:
            return dictionary.pop(key)
        for _, value in dictionary.items():
            if isinstance(value, dict):
                return IterationConfigGenerator.pop_dict_property(value, key)
        return None

    @classmethod
    def __generate_iterated_config(cls, config: Dict[str, Any], index: int) -> Dict[str, Any]:
        new_config = deepcopy(config)
        root_key = next(iter(new_config))
        new_key = re.sub(pattern=cls.ITERATION_REGEX, repl=str(index), string=root_key)
        new_config[new_key] = new_config.pop(root_key)

        def replace_iteration_index(new_config: Dict[str, Any]) -> None:
            for key, value in new_config.items():
                if isinstance(value, str):
                    new_value = re.sub(
                        pattern=cls.ITERATION_INDEX_REGEX, repl=str(index), string=value
                    )
                    if new_value != value:
                        new_config[key] = new_value
                elif isinstance(value, dict):
                    replace_iteration_index(value)

        replace_iteration_index(new_config=new_config)
        return new_config
