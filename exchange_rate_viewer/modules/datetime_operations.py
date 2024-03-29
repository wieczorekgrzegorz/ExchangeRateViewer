"""Module for date and time operations."""
import datetime

from modules import config


def get_difference_in_days(start_date: str, end_date: str) -> int:
    """Calculate difference in days between two dates."""
    return (str_to_date(date_str=end_date) - str_to_date(date_str=start_date)).days


def str_to_date(date_str: str) -> datetime.date:
    """Convert date string to datetime object."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def date_to_str(date_obj: datetime.date) -> str:
    """Convert date object to string."""
    return date_obj.strftime("%Y-%m-%d")


def today_and_yesterday() -> tuple[datetime.date, datetime.date]:
    """Return today's and yesterday's date."""
    return datetime.datetime.now().date(), datetime.datetime.now().date() - datetime.timedelta(days=1)


def get_max_date_range() -> datetime.timedelta:
    """Return maximum date range allowed by NBP API."""
    return datetime.timedelta(days=config.MAX_DATE_RANGE)


def add_days_to_date(date_obj: datetime.date, days: int) -> datetime.date:
    """Add days to datetime.date object."""
    return date_obj + datetime.timedelta(days=days)


def start_date_after_end_date(start_date: str, end_date: str) -> bool:
    """Check if start date is after end date."""
    return str_to_date(date_str=start_date) > str_to_date(date_str=end_date)


def max_range_exceeded(start_date: str, end_date: str, max_range: datetime.timedelta) -> bool:
    """Check if the date range exceeds the maximum allowed by NBP API."""
    return str_to_date(date_str=end_date) - str_to_date(date_str=start_date) > max_range


def date_not_weekend(date_to_check: datetime.date) -> bool:
    """Check if date is not a weekend."""
    return date_to_check.isoweekday() < 6


def define_all_days_to_check(start_date: str, days_difference: int) -> list[str]:
    """Collect dates to check for data in local database. Excludes weekends."""
    days_to_check = []

    for i in range(days_difference):
        new_date = add_days_to_date(date_obj=str_to_date(date_str=start_date), days=i)

        if date_not_weekend(date_to_check=new_date):
            days_to_check.append(start_date)

    return days_to_check
