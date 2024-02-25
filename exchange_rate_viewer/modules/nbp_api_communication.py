"""Module for communication with NBP API."""

import logging

import requests

from modules import custom_exceptions, config


log = logging.getLogger(name="log." + __name__)


def connect_with_nbp_api(url: str, error_message: str) -> requests.Response:
    """Connects with NBP API using given url and returns the response.

    Raises:
        custom_exceptions.NBPConnectionError: If failed to connect with NBP API.
            Uses error_message as the exception message.
    """
    log.debug(msg=f"Sending GET request to NBP API, url: {url}")

    try:
        response = requests.get(url=url, timeout=config.REQUEST_TIMEOUT)
        log.debug(msg=f"Response from NBP API ({response.status_code}, {response.reason}): {response.text}")
    except requests.exceptions.RequestException as exc:
        log.exception(msg=exc)
        raise custom_exceptions.NBPConnectionError(message=error_message) from exc

    return response


def check_nbp_response(response: requests.Response, general_error_message: str, error_404_message: str) -> None:
    """Checks if the response from NBP API is valid.

    Raises:
        custom_exceptions.NBPConnectionError: If the response from NBP API is not valid.
            Uses error_message as the exception message.
    """

    if response.status_code == 404:
        raise custom_exceptions.NBPConnectionError(message=error_404_message)

    if response.status_code != 200:
        log_message = f"NBP API response (<{response.status_code}, {response.reason}>): {response.text}"
        log.warning(msg=log_message)
        raise custom_exceptions.NBPConnectionError(message=general_error_message)

    log.info(msg=f"Request successfull, status code: {response.status_code}, {response.reason}.")


def get_list_of_currency_dicts_from(nbp_response: requests.Response) -> list[dict]:
    """Converts the response to a list of dictionaries.

    NBP API response to fetch_available_currencies() returns a table in format of one-element list with
    a dictionary containing keys: table, no, effectiveDate, rates.
    Example:
        [{
            'table': 'A',
            'no': '034/A/NBP/2024',
            'effectiveDate': '2024-02-16',
            'rates': [
                {'currency': 'bat (Tajlandia)', 'code': 'THB', 'mid': 0.112},
                {'currency': 'dolar amerykański', 'code': 'USD', 'mid': 4.0325},
                ...,
                {'currency': 'SDR (MFW)', 'code': 'XDR', 'mid': 5.3457}
            ]
        }]
    Converts the response to a list of dictionaries. Takes first (the only) element of the list and returns the value
    of the 'rates' key. The value is a list of dictionaries containing keys: currency, code, mid.

    Parameters:
        nbp_response (requests.Response): Response from NBP API.

    Returns:
        list[dict]: List of dictionaries containing keys: 'currency', 'code', 'mid'.
    """
    return nbp_response.json()[0].get("rates")


def get_available_currencies_from(rates: list[dict]) -> list[str]:
    """Extracts currency codes from the list of NBP rates.

    Parameters:
        rates (list[dict]): List of dictionaries containing keys: 'currency', 'code', 'mid'.
    """
    available_currencies = [rate["code"] for rate in rates]
    available_currencies.sort()

    return available_currencies


def fetch_available_currencies() -> list[str]:
    """Fetches available currencies from NBP API.

    Returns:
        list[str]: List of currency codes available in NBP API.

    Raises:
        custom_exceptions.NBPConnectionError: If failed to fetch available currencies from NBP API.
    """
    error_message = "Failed to fetch available currencies from NBP API, check connection with NBP API."

    log.info(msg="Fetching available currencies from NBP API.")
    response = connect_with_nbp_api(url=config.NBP_TABLES_URL, error_message=error_message)
    print(f"available_currencies: {response.text}")
    check_nbp_response(response=response, general_error_message=error_message, error_404_message=error_message)
    rates = get_list_of_currency_dicts_from(nbp_response=response)
    available_currencies = get_available_currencies_from(rates=rates)

    return available_currencies


def build_url(currency: str, start_date: str, end_date: str) -> str:
    """Builds NBP API URL for fetching currency exchange rates.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
    """
    return config.NBP_RATES_URL + f"{currency}/{start_date}/{end_date}"


def convert_response_to_json(nbp_api_response: requests.Response) -> dict:
    """Converts response from NBP API to JSON format."""
    return nbp_api_response.json()


def convert_nbp_response_to_list_of_exchange_rates(response_json: dict, currency: str) -> list[tuple]:
    """Converts currency rates from NBP API to a list of tuples for insertion into the local database."""
    rows_to_insert = []

    for item in response_json["rates"]:
        effective_date = item["effectiveDate"]
        rate = item["mid"]
        rows_to_insert.append((effective_date, currency, rate))

    return rows_to_insert


def fetch_currency_rates(currency: str, start_date: str, end_date: str) -> list[tuple[str, str, str]]:
    """Fetches currency exchange rates from NBP API.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.

    Returns:
        list[tuple]: List of tuples containing date, currency code and exchange rate.

    Raises:
        custom_exceptions.NBPConnectionError: If failed to fetch currency exchange rates from NBP API.
    """
    general_error_message = "Failed to fetch currency exchange rates from NBP API, check connection with NBP API."
    error_404_message = "Error 404: No data found for selected currency and/or time frame."

    log.info(msg=f"Fetching currency exchange rates from NBP API ({currency}/PLN, {start_date}, {end_date}).")
    url = build_url(currency=currency, start_date=start_date, end_date=end_date)
    response = connect_with_nbp_api(url=url, error_message=general_error_message)

    print(f"Currency rates: {response.text}")

    check_nbp_response(
        response=response, general_error_message=general_error_message, error_404_message=error_404_message
    )

    response_json = convert_response_to_json(nbp_api_response=response)

    return convert_nbp_response_to_list_of_exchange_rates(response_json=response_json, currency=currency)
