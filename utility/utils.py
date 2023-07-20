import pandas as pd

from utility.logger import get_logger

LOGGER = get_logger("Utils Module.")


def get_latest_values(raw_data: pd.DataFrame):
    sorted_data = raw_data.sort_values("time_stamp").reset_index()
    LOGGER.info("Raw data has been sorted as per 'time_stamp' column.")

    grouped_sorted_data = sorted_data.groupby("device_fk_id")
    LOGGER.info("Sorted data has been grouped by 'device_fk_id'")

    for entry in list(grouped_sorted_data):
        latest_time = entry[1]["time_stamp"].max()
        LOGGER.info(f"Latest time for {entry[0]} is {latest_time}")
        LOGGER.info(f"Entire row:\n{entry[1].tail(1)}")
