import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

DateRange = Tuple[datetime.datetime, datetime.datetime]


def create_fallback_date_range() -> DateRange:
    """
    Returns:
        Tuple[datetime.datetime, datetime.datetime]: A date range corresponding to the time between now and
        one year ago.
    """
    end_time = datetime.datetime.now()
    start_time = end_time - relativedelta(years=1)

    return start_time, end_time


def parse_date_str_to_datetime(date_str: str) -> datetime.datetime:
    """
    Parses a date string into a datetime object.

    Args:
        date_str (str): A string representing the date in the format 'YYYY-MM-DD' or 'YYYYMMDD'.

    Returns:
        datetime: A datetime object corresponding to the given date string.
    """
    if "-" in date_str:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    else:
        return datetime.datetime.strptime(date_str, "%Y%m%d")
