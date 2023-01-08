import argparse
import logging

from melanoma_phd.MelanomaPhdApp import create_melanoma_phd_app

APP_LOGGING_FILE_NAME = "melanoma_phd_app.log"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Melanoma PHD application")
    parser.add_argument("--debug_trace", action="store_true", help="print all logging messages")
    parser.add_argument("--no_trace", action="store_true", help="no logging messages")
    parser.add_argument("--log_filename", metavar="log_filename", help="filename of the logs")
    args = parser.parse_args()

    debug_trace = args.debug_trace
    no_trace = args.no_trace
    log_filename = args.log_filename
    logger_level = logging.CRITICAL if no_trace else logging.DEBUG if debug_trace else logging.INFO
    logger_file = log_filename if log_filename else APP_LOGGING_FILE_NAME
    app = create_melanoma_phd_app(log_filename=logger_file, log_level=logger_level)
    errors = app.database.check_data_integrity()
    if errors:
        error_string = [
            f"'{error.column}' | '{error.source_sheet}' - '{error.target_sheet}' values mismatch"
            for error in errors
        ]
        logging.error("DATABASE INTEGRITY ERRORS FOUND!\n" + "\n".join(error_string))
