import os
import pickle
import zlib
from pathlib import Path

import pandas as pd
import redis
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from utility.constants import Constants
from utility.logger import get_logger
from utility.utils import get_latest_values

LOGGER = get_logger("Main Module.")

FILE = Path(__file__).resolve()
ROOT_DIR = FILE.parents[0]

app = FastAPI(debug=True)

r = redis.Redis(host="redis", port=6379)


@app.on_event("startup")
def store_latest_data():
    # Read raw data
    raw_data = pd.read_csv(os.path.join(ROOT_DIR, Constants.RAW_DATA_PATH.value))

    r.set("raw_data", zlib.compress(pickle.dumps(raw_data)))

    # Getting and storing the latest values as per the timestamp of each device id
    latest_values = get_latest_values(raw_data)
    LOGGER.info(f"Latest Values DF :\n{latest_values}")

    r.set("latest_values", zlib.compress(pickle.dumps(latest_values)))

    fetch_latest = pickle.loads(zlib.decompress(r.get("latest_values")))
    LOGGER.info(f"Latest values fetched from cache successfully - {fetch_latest}")


@app.get("/latest_device_info")
def get_latest_device_info(device_fk_id: int):
    latest_values = pickle.loads(zlib.decompress(r.get("latest_values")))
    LOGGER.info(f"Latest values fetched - {latest_values.head()}")

    valid_row = (
        latest_values.loc[latest_values["device_fk_id"] == device_fk_id]
        .drop(["level_0", "index"], axis=1)
        .reset_index()
    )
    LOGGER.info(f"Valid row -> {valid_row}")

    response = {
        "device_fk_id": str(valid_row.device_fk_id[0]),
        "latitude": str(valid_row.latitude[0]),
        "longitude": str(valid_row.longitude[0]),
        "time_stamp": str(valid_row.time_stamp[0]),
        "sts": str(valid_row.sts[0]),
        "speed": str(valid_row.speed[0]),
    }
    return JSONResponse(content=response, status_code=200)


# if __name__ == "__main__":
#     uvicorn.run("main:app", port=8000, log_level="info", reload=True)
