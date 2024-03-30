"""Unit tests for app.py."""

import datetime
import os
import unittest
from unittest.mock import patch

from test import _context  # pylint: disable=C0411:wrong-import-order

with patch.dict(os.environ, _context.mock_env_vars):
    from exchange_rate_viewer import app


class TestGetDatesFrom(unittest.TestCase):
    """Test get_dates_from function."""

    def test_get_dates_from(self) -> None:
        """Test get_dates_from function."""
        currency_table = [
            ("2021-01-01", 1.0),
            ("2021-01-02", 2.0),
            ("2021-01-03", 3.0),
        ]

        result = app.get_dates_from(currency_table=currency_table)
        expected = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
        ]

        self.assertEqual(first=result, second=expected)

    def test_get_dates_from_empty(self) -> None:
        """Test get_dates_from function with empty currency_table."""
        currency_table = []

        result = app.get_dates_from(currency_table=currency_table)
        expected = []

        self.assertEqual(first=result, second=expected)


class TestDataAlreadyInCache(unittest.TestCase):
    """Test data_already_in_cache function."""

    def test_data_already_in_cache(self) -> None:
        """Test data_already_in_cache function."""
        dates_from_currency_table = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
        ]
        days_to_check = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
        ]

        result = app.data_already_in_cache(
            dates_from_currency_table=dates_from_currency_table, days_to_check=days_to_check
        )
        expected = True

        self.assertEqual(first=result, second=expected)

    def test_data_already_in_cache_not_in_cache(self) -> None:
        """Test data_already_in_cache function with dates not in cache."""
        dates_from_currency_table = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
        ]
        days_to_check = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
            datetime.date(year=2021, month=1, day=4),
        ]

        result = app.data_already_in_cache(
            dates_from_currency_table=dates_from_currency_table, days_to_check=days_to_check
        )
        expected = False

        self.assertEqual(first=result, second=expected)

    def test_data_already_in_cache_empty(self) -> None:
        """Test data_already_in_cache function with empty dates_from_currency_table."""
        dates_from_currency_table = []
        days_to_check = [
            datetime.date(year=2021, month=1, day=1),
            datetime.date(year=2021, month=1, day=2),
            datetime.date(year=2021, month=1, day=3),
        ]

        result = app.data_already_in_cache(
            dates_from_currency_table=dates_from_currency_table, days_to_check=days_to_check
        )
        expected = False

        self.assertEqual(first=result, second=expected)
