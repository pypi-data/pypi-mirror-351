import os
from datetime import datetime, timedelta

import pandas as pd
from dateutil.relativedelta import relativedelta

from dst_handler_ogre.constants import FREQUENCY_ENTRY_DICT, Resolution

tz_converted_df_path = "{park_name}_tz_converted_df.p"

NUMBER_OF_HOURS_IN_DAY = 24


def get_last_sunday_of_month(year: int, month: int):
    # Find the first day of the next month
    first_day_of_next_month = datetime(year, month, 1) + relativedelta(months=1)

    # Calculate the last day of the current month
    last_day_of_current_month = (first_day_of_next_month - timedelta(days=1)).date()

    # Find the weekday of the last day of the month (Monday is 0 and Sunday is 6)
    weekday = last_day_of_current_month.weekday()

    # Calculate the number of days to subtract to get to the last Saturday
    days_to_subtract = (weekday - 6) % 7

    # Calculate the date of the last Saturday
    last_saturday_date = last_day_of_current_month - timedelta(days=days_to_subtract)

    return datetime.combine(last_saturday_date, datetime.min.time())


def march_dst_handler(df: pd.DataFrame, year: int, entries_per_hour: int) -> pd.DataFrame:
    """
    1. if we don't have the expected number of intervals (92), but we have 96 intervals we must delete the extra hour
    2. if we have the expected number of intervals we must check that the last timestamp of the day is indeed the last
    timestamp of the day, otherwise we need to shift all timestamp starting from 3:00 by one hour
    """
    last_sunday_of_march = get_last_sunday_of_month(year, 3)
    dst_timestamp_start = last_sunday_of_march + timedelta(hours=3)
    dst_timestamp_end = last_sunday_of_march + timedelta(hours=4)
    dst_day_df = df[(df.index >= last_sunday_of_march) & (df.index < last_sunday_of_march + timedelta(days=1))]
    expected_number_of_intervals = entries_per_hour * NUMBER_OF_HOURS_IN_DAY - entries_per_hour
    if len(dst_day_df) == 0:
        return df
    if len(dst_day_df) == expected_number_of_intervals + entries_per_hour:  # if there 96 intervals we delete the extra hour
        df = df[~((df.index >= dst_timestamp_start) & (df.index < dst_timestamp_end))]
    elif len(dst_day_df) == expected_number_of_intervals:
        if dst_day_df.index[-1].hour != 23:
            dst_day_df.index = dst_day_df.index.map(lambda idx: idx if idx.hour < 3 else idx + timedelta(hours=1))
            df = pd.concat([df[~((df.index >= last_sunday_of_march) & (df.index < last_sunday_of_march + timedelta(days=1)))], dst_day_df])
    else:
        # TODO - what happens when the day has too few intervals
        print("TODO")
    return df


def october_dst_handler(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    October has the interval 3:00-4:00 twice in the last Sunday of the month.
    We need to subtract 1 hour from each timestamp of this sunday until the second 3:00-4:00 interval in order to remove
    the extra summertime hour.
    """
    last_sunday_of_october = get_last_sunday_of_month(year, 10)
    dst_day_df = df[(df.index >= last_sunday_of_october) & (df.index < last_sunday_of_october + timedelta(days=1))]
    duplicated_indices = dst_day_df.index.duplicated(keep="last")
    dst_day_df["adjusted_index"] = dst_day_df.index
    dst_day_df.loc[duplicated_indices, "adjusted_index"] -= pd.Timedelta(hours=1)
    dst_hours = dst_day_df.set_index("adjusted_index")
    dst_hours.index.name = "timestamp"
    df = pd.concat([df[~((df.index >= last_sunday_of_october) & (df.index < last_sunday_of_october + timedelta(days=1)))], dst_hours]).sort_index()
    return df


def remove_extra_summer_hour(df: pd.DataFrame, year: int) -> pd.DataFrame:
    first_eest_datetime = get_last_sunday_of_month(year, 3) + timedelta(hours=4)
    last_eest_datetime = get_last_sunday_of_month(year, 10) + timedelta(hours=3)
    df.index = df.index.map(lambda idx: idx - timedelta(hours=1) if first_eest_datetime <= idx < last_eest_datetime else idx)
    df = october_dst_handler(df, year)
    return df


def validate_resolution(resolution_str: str):
    if resolution_str not in [Resolution.FIVE_MINUTES.value, Resolution.TEN_MINUTES.value, Resolution.QUARTER_HOUR.value, Resolution.HALF_HOUR.value, Resolution.HOUR.value]:
        raise Exception(f"Unknown resolution {resolution_str}")
    return Resolution(resolution_str)


def convert_eet_to_utc(df: pd.DataFrame, resolution_str: str) -> pd.DataFrame:
    resolution = validate_resolution(resolution_str)
    for year in range(df.index.min().year, df.index.max().year + 1):
        df = march_dst_handler(df, year, FREQUENCY_ENTRY_DICT[resolution])
        df = remove_extra_summer_hour(df, year)
    df.index -= pd.Timedelta(hours=2)
    return df
