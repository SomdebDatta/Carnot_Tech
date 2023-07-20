import os
import tomllib
from enum import Enum
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT_DIR = FILE.parents[1]


class Constants(Enum):
    CONFIG_PATH = os.path.join("config", "config.toml")

    with open(ROOT_DIR / CONFIG_PATH, mode="rb") as reader:
        toml_file_dict = tomllib.load(reader)

    LOGGER_FILE_NAME = toml_file_dict.get("log")

    LOGGING_FORMAT = "%(process)d-%(levelname)s-%(message)s"

    RAW_DATA_PATH = os.path.join("config", "Raw Data - Backend Developer. (1).csv")
