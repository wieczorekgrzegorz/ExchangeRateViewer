""""""

import datetime
import os
import unittest
from unittest.mock import patch

from test import _context

with patch.dict(os.environ, _context.mock_env_vars):
    from exchange_rate_viewer.modules import datetime_operations


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


if __name__ == "__main__":
    unittest.main()
