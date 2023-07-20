import os
import pickle
import zlib
from pathlib import Path

import pandas as pd
import redis
from fastapi import FastAPI, HTTPException, status

from utility.constants import Constants
from utility.logger import get_logger
from utility.utils import get_latest_values

LOGGER = get_logger("Main Module.")

FILE = Path(__file__).resolve()
ROOT_DIR = FILE.parents[0]

app = FastAPI(debug=True)


@app.on_event("startup")
def store_latest_data():
    # Read raw data
    raw_data = pd.read_csv(os.path.join(ROOT_DIR, Constants.RAW_DATA_PATH.value))

    # Getting and storing the latest values as per the timestamp of each device id
    latest_values = get_latest_values(raw_data)
    LOGGER.info(f"Latest Values DF :\n{latest_values}")

    r = redis.Redis(host="redis", port=6379)

    r.set("latest_values", zlib.compress(pickle.dumps(latest_values)))

    fetch_latest = pickle.loads(zlib.decompress(r.get("latest_values")))
    LOGGER.info(f"Latest values fetched from cache successfully - {fetch_latest}")


@app.get("/latest_device_info")
def get_latest_device_info():
    pass
