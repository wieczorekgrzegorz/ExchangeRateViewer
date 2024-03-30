"""Unit tests for datetime_operations module."""

import logging
import os
import unittest
from unittest.mock import patch

from test import _context

import requests


with patch.dict(os.environ, _context.mock_env_vars):
    from exchange_rate_viewer.modules import nbp_api_communication, config


class TestConnectWithNBPApi(unittest.TestCase):
    """Test connect_with_nbp_api function."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        logging.disable(level=logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        logging.disable(level=logging.NOTSET)

    @patch("exchange_rate_viewer.modules.nbp_api_communication.requests.get")
    def test_connect_with_nbp_api(self, mock_requests_get) -> None:
        """Test connect_with_nbp_api function."""
        url = "http://example.com"
        error_message = "Error message"

        response = nbp_api_communication.connect_with_nbp_api(url=url, error_message=error_message)

        mock_requests_get.assert_called_once_with(url=url, timeout=config.REQUEST_TIMEOUT)

        self.assertEqual(first=response, second=mock_requests_get.return_value)

    @patch("exchange_rate_viewer.modules.nbp_api_communication.requests.get")
    def test_connect_with_nbp_api_connection_error(self, mock_requests_get) -> None:
        """Test connect_with_nbp_api function with ConnectionError."""
        url = "http://example.com"
        error_message = "Error message"

        response = requests.Response()
        response.status_code = 404
        response._content = b"Content"  # pylint: disable=protected-access

        mock_requests_get.side_effect = requests.exceptions.RequestException()
        expected_exception = nbp_api_communication.custom_exceptions.NBPConnectionError

        with self.assertRaises(expected_exception=expected_exception):
            nbp_api_communication.connect_with_nbp_api(url=url, error_message=error_message)


class TestCheckNBPResponse(unittest.TestCase):
    """Test check_nbp_response function."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        logging.disable(level=logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        logging.disable(level=logging.NOTSET)

    @patch("exchange_rate_viewer.modules.nbp_api_communication.log")
    def test_check_nbp_response_200(self, mock_log) -> None:
        """Test check_nbp_response function with 200 status code."""
        response = requests.Response()
        response.status_code = 200
        response._content = b"Content"  # pylint: disable=protected-access

        general_error_message = "General error message"
        error_404_message = "404 error message"

        nbp_api_communication.check_nbp_response(
            response=response, general_error_message=general_error_message, error_404_message=error_404_message
        )

        mock_log.info.assert_called_once()
        mock_log.warning.assert_not_called()

    @patch("exchange_rate_viewer.modules.nbp_api_communication.log")
    def test_check_nbp_response_404(self, mock_log) -> None:
        """Test check_nbp_response function with 404 status code."""
        response = requests.Response()
        response.status_code = 404
        response._content = b"Content"  # pylint: disable=protected-access

        general_error_message = "General error message"
        error_404_message = "404 error message"

        expected_exception = nbp_api_communication.custom_exceptions.NBPConnectionError

        with self.assertRaises(expected_exception=expected_exception):
            nbp_api_communication.check_nbp_response(
                response=response, general_error_message=general_error_message, error_404_message=error_404_message
            )

        mock_log.info.assert_not_called()
        mock_log.warning.assert_called_once()


class TestGetListOfCurrencyDictsFrom(unittest.TestCase):
    """Test get_list_of_currency_dicts_from function."""

    def test_get_list_of_currency_dicts_from(self) -> None:
        """Test get_list_of_currency_dicts_from function."""
        response = requests.Response()

        # pylint: disable=line-too-long
        content = b'[{"table": "A", "no": "001/A/NBP/2021", "effectiveDate": "2021-01-04", "rates": [{"currency": "bat (Tajlandia)", "code": "THB", "mid": 0.112}, {"currency": "dolar amerykanski", "code": "USD", "mid": 4.0325}, {"currency": "SDR (MFW)", "code": "XDR", "mid": 5.3457}]}]'

        response._content = content  # pylint: disable=protected-access

        result = nbp_api_communication.get_list_of_currency_dicts_from(nbp_response=response)
        expected = [
            {"code": "THB", "currency": "bat (Tajlandia)", "mid": 0.112},
            {"code": "USD", "currency": "dolar amerykanski", "mid": 4.0325},
            {"code": "XDR", "currency": "SDR (MFW)", "mid": 5.3457},
        ]

        self.assertEqual(first=result, second=expected)


class TestGetAvailableCurrenciesFrom(unittest.TestCase):
    """Test get_available_currencies_from function."""

    def test_get_available_currencies_from(self) -> None:
        """Test get_available_currencies_from function."""
        rates = [
            {"code": "THB", "currency": "bat (Tajlandia)", "mid": 0.112},
            {"code": "USD", "currency": "dolar amerykanski", "mid": 4.0325},
            {"code": "XDR", "currency": "SDR (MFW)", "mid": 5.3457},
        ]

        result = nbp_api_communication.get_available_currencies_from(rates=rates)
        expected = ["THB", "USD", "XDR"]

        self.assertEqual(first=result, second=expected)


class TestFetchAvailableCurrencies(unittest.TestCase):
    """Test fetch_available_currencies function."""

    @patch("exchange_rate_viewer.modules.nbp_api_communication.connect_with_nbp_api")
    @patch("exchange_rate_viewer.modules.nbp_api_communication.get_list_of_currency_dicts_from")
    @patch("exchange_rate_viewer.modules.nbp_api_communication.get_available_currencies_from")
    def test_fetch_available_currencies(
        self, mock_get_available_currencies_from, mock_get_list_of_currency_dicts_from, mock_connect_with_nbp_api
    ) -> None:
        """Test fetch_available_currencies function."""

        mock_response = requests.Response()
        mock_response.status_code = 200

        # pylint: disable=W0212:protected-access, C0301:line-too-long
        mock_response._content = b'[{"table": "A", "no": "001/A/NBP/2021", "effectiveDate": "2021-01-04", "rates": [{"currency": "bat (Tajlandia)", "code": "THB", "mid": 0.112}]}]'
        mock_connect_with_nbp_api.return_value = mock_response
        mock_get_list_of_currency_dicts_from.return_value = [
            {"code": "THB", "currency": "bat (Tajlandia)", "mid": 0.112}
        ]
        mock_get_available_currencies_from.return_value = ["THB"]

        result = nbp_api_communication.fetch_available_currencies()
        expected = ["THB"]

        self.assertEqual(first=result, second=expected)
