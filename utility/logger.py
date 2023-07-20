""" Copyright © Siemens AG 2023 ALL RIGHTS RESERVED. """
import logging
import logging.handlers
from logging import Logger
from pathlib import Path

from utility.constants import Constants

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]


def get_logger(name: str) -> Logger:
    logging.basicConfig(format=Constants.LOGGING_FORMAT.value)

    LOGGER = logging.getLogger(name)

    log_level = "DEBUG"

    handler_file = logging.handlers.RotatingFileHandler(
        Constants.LOGGER_FILE_NAME.value,
        mode="a",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding=None,
        delay=0,
    )

    log_formatter = logging.Formatter(
        "%(asctime)s -- %(levelname)s -- %(name)s -- %(funcName)s -- (%(lineno)d) -- %(message)s"
    )

    handler_file.setFormatter(log_formatter)

    if log_level == "DEBUG":
        LOGGER.setLevel(logging.DEBUG)
        handler_file.setLevel(logging.DEBUG)
    elif log_level == "ERROR":
        LOGGER.setLevel(logging.ERROR)
        handler_file.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)
        handler_file.setLevel(logging.INFO)

    LOGGER.addHandler(handler_file)
    return LOGGER
