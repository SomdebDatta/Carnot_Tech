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

    # Store raw data in cache
    r.set("raw_data", zlib.compress(pickle.dumps(raw_data)))

    # Getting and storing the latest values as per the timestamp of each device id
    (latest_values, start_end_values, grouped_data) = get_latest_values(raw_data)

    LOGGER.info("Caching all relevant data in redis.")
    r.set("latest_values", zlib.compress(pickle.dumps(latest_values)))

    r.set("start_end_values", zlib.compress(pickle.dumps(start_end_values)))

    r.set("grouped_data", zlib.compress(pickle.dumps(grouped_data)))

    LOGGER.info("Caching complete. Try out the APIs.")


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
    try:
        latest_values = pickle.loads(zlib.decompress(r.get("latest_values")))
        LOGGER.info("Latest values fetched.")

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

    except KeyError:
        LOGGER.error(f"This device id - {device_fk_id} does not exist!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect device id.",
        )


@app.get("/start_end_loc")
def get_start_end_loc(device_fk_id: int) -> dict:
    """
    This is the second API.
    Description as per document:
    An API that takes device ID and returns start location & end location for that device.
    Location should be (lat, lon) tuple.

    Args:
    :param `device_fk_id`: An integer specifying the device id.

    Returns:
    :returns `response`: A JSON response containing the relevant details as per the description above.
    """
    start_end_df = pickle.loads(zlib.decompress(r.get("start_end_values")))
    LOGGER.info("Start-End values fetched.")

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
    """
    This is the third API.
    Description as per document:
    An API that takes in device ID, start time & end time and returns all the location
    points as list of latitude, longitude & time stamp.

    Args:
    :param `device_fk_id`: An integer specifying the device id.
    :param `start_time`: A string specifying the start time.
    :param `end_time`: A string specifying the end time.

    Returns:
    :returns `response`: A JSON response containing the relevant details as per the description above.
    """
    data_list = []
    start_time_obj = parser.parse(start_time)
    end_time_obj = parser.parse(end_time)

    if start_time_obj < end_time_obj:
        grouped_data = pickle.loads(zlib.decompress(r.get("grouped_data")))
        LOGGER.info("Grouped data fetched.")

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
