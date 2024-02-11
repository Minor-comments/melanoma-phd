import logging
import os
from typing import List


def init_logger(
    log_filename: str = None,
    log_level: int = logging.DEBUG,
    custom_handlers: List[logging.Handler] = None,
) -> None:
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_filename:
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        handlers += [logging.FileHandler(log_filename)]
    if custom_handlers:
        handlers += custom_handlers
    logging.basicConfig(handlers=handlers, level=log_level)
