import logging
import os


def init_logger(log_filename: str = None, log_level: int = logging.DEBUG) -> None:
    handlers = [logging.StreamHandler()]
    if log_filename:
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        handlers += [logging.FileHandler(log_filename)]
    logging.basicConfig(handlers=handlers, level=log_level)
