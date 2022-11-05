import logging


def init_logger(log_filename: str = None, log_level: int = logging.DEBUG) -> None:
    handlers = (
        [logging.StreamHandler()] + [logging.FileHandler(log_filename)] if log_filename else []
    )
    logging.basicConfig(handlers=handlers, level=log_level)
