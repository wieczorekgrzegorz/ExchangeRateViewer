"""Unit tests for datetime_operations module."""

import datetime
import os
import unittest
from unittest.mock import patch

from freezegun import freeze_time

from test import _context  # pylint: disable=C0411:wrong-import-order

with patch.dict(os.environ, _context.mock_env_vars):
    from exchange_rate_viewer.modules import datetime_operations, config


class TestGetDifferenceInDays(unittest.TestCase):
    """Test get_difference_in_days function."""

    def test_get_difference_in_days(self) -> None:
        """Test get_difference_in_days function."""
        start_date = datetime.date(year=2021, month=1, day=1)
        end_date = datetime.date(year=2021, month=1, day=10)

        result = datetime_operations.get_difference_in_days(start_date=start_date, end_date=end_date)
        expected = 9

        self.assertEqual(first=result, second=expected)

    def test_get_difference_in_days_negative(self) -> None:
        """Test get_difference_in_days function with negative result."""
        start_date = datetime.date(year=2021, month=1, day=10)
        end_date = datetime.date(year=2021, month=1, day=1)

        result = datetime_operations.get_difference_in_days(start_date=start_date, end_date=end_date)
        expected = -9

        self.assertEqual(first=result, second=expected)


class TestAddDaysToDate(unittest.TestCase):
    """Test add_days_to_date function."""

    def test_add_days_to_date(self) -> None:
        """Test add_days_to_date function."""
        date_obj = datetime.date(year=2021, month=1, day=1)
        days = 10

        result = datetime_operations.add_days_to_date(date_obj=date_obj, days=days)
        expected = datetime.date(year=2021, month=1, day=11)

        self.assertEqual(first=result, second=expected)

    def test_add_days_to_date_negative(self) -> None:
        """Test add_days_to_date function with negative result."""
        date_obj = datetime.date(year=2021, month=1, day=1)
        days = -10

        result = datetime_operations.add_days_to_date(date_obj=date_obj, days=days)
        expected = datetime.date(year=2020, month=12, day=22)

        self.assertEqual(first=result, second=expected)


class TestDateNotWeekend(unittest.TestCase):
    """Test date_not_weekend function."""

    def test_date_not_weekend(self) -> None:
        """Test date_not_weekend function."""
        date_to_check = datetime.date(year=2021, month=1, day=1)

        result = datetime_operations.date_not_weekend(date_to_check=date_to_check)
        expected = True

        self.assertEqual(first=result, second=expected)

    def test_date_not_weekend_weekend(self) -> None:
        """Test date_not_weekend function with weekend date."""
        date_to_check = datetime.date(year=2021, month=1, day=2)

        result = datetime_operations.date_not_weekend(date_to_check=date_to_check)
        expected = False

        self.assertEqual(first=result, second=expected)


class TestDefineAllDaysToCheck(unittest.TestCase):
    """Test define_all_days_to_check function."""

    def test_define_all_days_to_check(self) -> None:
        """Test define_all_days_to_check function."""
        start_date = datetime.date(year=2021, month=1, day=1)
        days_difference = 10

        result = datetime_operations.define_all_days_to_check(start_date=start_date, days_difference=days_difference)

        expected = ["2021-01-01", "2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07", "2021-01-08"]

        self.assertEqual(first=result, second=expected)


class TestStrToDate(unittest.TestCase):
    """Test str_to_date function."""

    def test_str_to_date(self) -> None:
        """Test str_to_date function."""
        date_str = "2021-01-01"

        result = datetime_operations.str_to_date(date_str=date_str)
        expected = datetime.date(year=2021, month=1, day=1)

        self.assertEqual(first=result, second=expected)


class TestDateToStr(unittest.TestCase):
    """Test date_to_str function."""

    def test_date_to_str(self) -> None:
        """Test date_to_str function."""
        date_obj = datetime.date(year=2021, month=1, day=1)

        result = datetime_operations.date_to_str(date_obj=date_obj)
        expected = "2021-01-01"

        self.assertEqual(first=result, second=expected)


class TestYesterday(unittest.TestCase):
    """Test yesterday function."""

    @freeze_time(time_to_freeze="2022-01-02")
    def test_yesterday(self) -> None:
        """Test yesterday function."""

        result = datetime_operations.yesterday()
        expected = datetime.date(2022, 1, 1)

        self.assertEqual(first=result, second=expected)


class TestGetMaxDateRange(unittest.TestCase):
    """Test get_max_date_range function."""

    def test_get_max_date_range(self) -> None:
        """Test get_max_date_range function."""

        result = datetime_operations.get_max_date_range()
        expected = datetime.timedelta(days=config.MAX_DATE_RANGE)

        self.assertEqual(first=result, second=expected)


class TestStartDateAfterEndDate(unittest.TestCase):
    """Test start_date_after_end_date function."""

    def test_start_date_after_end_date(self) -> None:
        """Test start_date_after_end_date function."""
        start_date = "2021-01-10"
        end_date = "2021-01-01"

        result = datetime_operations.start_date_after_end_date(start_date=start_date, end_date=end_date)
        expected = True

        self.assertEqual(first=result, second=expected)

    def test_start_date_after_end_date_false(self) -> None:
        """Test start_date_after_end_date function with False result."""
        start_date = "2021-01-01"
        end_date = "2021-01-10"

        result = datetime_operations.start_date_after_end_date(start_date=start_date, end_date=end_date)
        expected = False

        self.assertEqual(first=result, second=expected)


class TestMaxRangeExceeded(unittest.TestCase):
    """Test max_range_exceeded function."""

    def test_max_range_exceeded(self) -> None:
        """Test max_range_exceeded function."""
        start_date = "2021-01-01"
        max_range = datetime.timedelta(days=93)
        end_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date() + datetime.timedelta(days=94)
        end_date = end_date.strftime("%Y-%m-%d")

        result = datetime_operations.max_range_exceeded(start_date=start_date, end_date=end_date, max_range=max_range)
        expected = True

        self.assertEqual(first=result, second=expected)

    def test_max_range_exceeded_false(self) -> None:
        """Test max_range_exceeded function with False result."""
        start_date = "2021-01-01"
        end_date = "2021-01-10"
        max_range = datetime.timedelta(days=93)

        result = datetime_operations.max_range_exceeded(start_date=start_date, end_date=end_date, max_range=max_range)
        expected = False

        self.assertEqual(first=result, second=expected)


if __name__ == "__main__":
    unittest.main()
