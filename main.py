import os
import pickle
import zlib
from pathlib import Path

import pandas as pd
import redis
import uvicorn
from dateutil import parser
from fastapi import FastAPI, HTTPException, status
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
    """
    This function will be executed on startup of the service.

    1. Read the raw data.
    2. Store the raw data in a redis cache.
    3. Calculate the latest data and store it in the cache.
    4. Calculate and store the grouped data for efficient calculations.
    5. Stores any other data in the cache that will be helpful for the APIs.

    """
    # Read raw data
    raw_data = pd.read_csv(os.path.join(ROOT_DIR, Constants.RAW_DATA_PATH.value))

    r.set("raw_data", zlib.compress(pickle.dumps(raw_data)))

    # Getting and storing the latest values as per the timestamp of each device id
    (latest_values, start_end_values, grouped_data) = get_latest_values(raw_data)
    LOGGER.info(f"Latest Values DF :\n{latest_values}")

    r.set("latest_values", zlib.compress(pickle.dumps(latest_values)))

    r.set("start_end_values", zlib.compress(pickle.dumps(start_end_values)))

    r.set("grouped_data", zlib.compress(pickle.dumps(grouped_data)))

    # fetch_latest = pickle.loads(zlib.decompress(r.get("latest_values")))
    # LOGGER.info(f"Latest values fetched from cache successfully - {fetch_latest}")


@app.get("/latest_device_info")
def get_latest_device_info(device_fk_id: int) -> dict:
    """
    This is the first API.
    Description as per document:
    An API that takes device ID and returns device's latest information in response.

    Args:
    :param `device_fk_id`: An integer specifying the device id.

    Returns:
    :returns `response`: A JSON response specifying all the latest details of the device.
    """
    latest_values = pickle.loads(zlib.decompress(r.get("latest_values")))
    LOGGER.info(f"Latest values fetched - \n{latest_values.head()}")

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


@app.get("/start_end_loc")
def get_start_end_loc(device_fk_id: int) -> dict:
    start_end_df = pickle.loads(zlib.decompress(r.get("start_end_values")))
    LOGGER.info(f"Start-End values fetched - \n{start_end_df.head()}")

    try:
        valid_rows = (
            start_end_df.loc[start_end_df["device_fk_id"] == device_fk_id]
            .drop(["index"], axis=1)
            .reset_index()
        )
        LOGGER.info(f"Start and End rows for {device_fk_id} are:\n{valid_rows}")

        response = {
            "device_id": device_fk_id,
            "start_location": [
                str(valid_rows.latitude[0]),
                str(valid_rows.longitude[0]),
            ],
            "end_location": [str(valid_rows.latitude[1]), str(valid_rows.longitude[1])],
        }
        return JSONResponse(content=response, status_code=200)
    except KeyError:
        LOGGER.error(f"This device id - {device_fk_id} does not exist!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect device id.",
        )


@app.get("/get_all_geometries")
def get_all_geometries(device_fk_id: int, start_time: str, end_time: str) -> dict:
    data_list = []
    start_time_obj = parser.parse(start_time)
    end_time_obj = parser.parse(end_time)

    if start_time_obj < end_time_obj:
        grouped_data = pickle.loads(zlib.decompress(r.get("grouped_data")))
        LOGGER.info(f"Grouped data fetched.")

        for entry in grouped_data:
            if entry[0] == device_fk_id:
                relevant_table = entry[1].reset_index()

        start_time_index = (
            relevant_table.loc[relevant_table["time_stamp"] == start_time]
            .drop(["index", "level_0"], axis=1)
            .index
        )
        end_time_index = (
            relevant_table.loc[relevant_table["time_stamp"] == end_time]
            .drop(["index", "level_0"], axis=1)
            .index
        )

        if not (start_time_index.empty or end_time_index.empty):
            for index in range(
                start_time_index.values[0], end_time_index.values[0] + 1
            ):
                data_list.append(
                    {
                        "location": (
                            relevant_table.iloc[index].latitude,
                            relevant_table.iloc[index].longitude,
                        ),
                        "time_stamp": relevant_table.iloc[index].time_stamp,
                    }
                )

            if data_list:
                response = {"device_id": device_fk_id, "location_points": data_list}

                return JSONResponse(content=response, status_code=200)
        else:
            LOGGER.error(f"Could not match the start and end time!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not match the start and end time!",
            )

    else:
        LOGGER.error(f"This device id - {device_fk_id} does not exist!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect device id.",
        )


# if __name__ == "__main__":
#     uvicorn.run("main:app", port=8000, log_level="info", reload=True)
