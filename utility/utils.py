import pandas as pd

from utility.logger import get_logger

LOGGER = get_logger("Utils Module.")


def get_latest_values(
    raw_data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    This is a helper function.
    On the startup of this service, this does the necessary calculations and
    stores in cache so as to save time when the APIs are called.

    Args:
    :param `raw_data`: A pandas DataFrame having the raw input data.

    Returns:
    :returns `response`: A tuple of 3 DataFrames containing relevant data required by
    the APIs."""
    sorted_data = raw_data.sort_values("time_stamp").reset_index()
    LOGGER.info("Raw data has been sorted as per 'time_stamp' column.")

    grouped_sorted_data = sorted_data.groupby("device_fk_id")
    LOGGER.info("Sorted data has been grouped by 'device_fk_id'")

    latest_df = pd.DataFrame()
    start_end_df = pd.DataFrame()
    for entry in list(grouped_sorted_data):
        oldest_time = entry[1]["time_stamp"].min()
        # LOGGER.info(f"Oldest time for {entry[0]} is {oldest_time}")

        oldest_row = entry[1].head(1)
        # LOGGER.info(f"Oldest row for {entry[0]} is {oldest_row}")

        latest_time = entry[1]["time_stamp"].max()
        # LOGGER.info(f"Latest time for {entry[0]} is {latest_time}")

        latest_row = entry[1].tail(1)
        # LOGGER.info(f"Latest row for {entry[0]} is {latest_row}")

        start_end_df = pd.concat([start_end_df, oldest_row], axis=0)
        start_end_df = pd.concat([start_end_df, latest_row], axis=0)

        latest_df = pd.concat([latest_df, latest_row], axis=0)

    return (latest_df.reset_index(), start_end_df.reset_index(), grouped_sorted_data)
