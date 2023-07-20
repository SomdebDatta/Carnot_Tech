import os
from pathlib import Path

import pandas as pd
import redis

from utility.constants import Constants
from utility.utils import get_latest_values

FILE = Path(__file__).resolve()
ROOT_DIR = FILE.parents[0]

# Read raw data
raw_data = pd.read_csv(os.path.join(ROOT_DIR, Constants.RAW_DATA_PATH.value))

# Getting and storing the latest values as per the timestamp of each device id
latest_values = get_latest_values(raw_data)


# r = redis.Redis(host="redis", port=6379, decode_responses=True)

# r.set("test_var", "test_value")
