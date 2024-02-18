"""Flask app for fetching and displaying currency exchange rates from NBP API."""
import logging
import datetime

import flask
from werkzeug.datastructures import ImmutableMultiDict

from modules import custom_exceptions, config, nbp_api_communication, plot, sqldb_communication

log = logging.getLogger(name="log." + __name__)
config.setup()


app = flask.Flask(import_name=__name__)


def str_to_date(date_str: str) -> datetime.date:
    """Convert date string to datetime object."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def date_to_str(date_obj: datetime.date) -> str:
    """Convert date object to string."""
    return date_obj.strftime("%Y-%m-%d")


def get_max_date_range() -> datetime.timedelta:
    """Return maximum date range allowed by NBP API."""
    return datetime.timedelta(days=config.MAX_DATE_RANGE)


def validate_user_input(
    request_form: ImmutableMultiDict[str, str], today: datetime.date, yesterday: datetime.date
) -> tuple[str, str, str]:
    """Validates user input from the form.

    Raises:
        custom_exceptions.InvalidInputError: If input is invalid.
    """
    error_message = None
    max_range = get_max_date_range()

    selected_currency = request_form.get(key="currency")

    if not selected_currency:
        error_message = "Please select a currency."
        raise custom_exceptions.InvalidInputError(message=error_message)

    start_date_str = request_form.get(key="start_date", default=date_to_str(date_obj=yesterday))
    end_date_str = request_form.get(key="end_date", default=date_to_str(date_obj=today))

    if str_to_date(date_str=start_date_str) > str_to_date(date_str=end_date_str):
        error_message = "'Start Date' cannot be after 'End Date'."
        raise custom_exceptions.InvalidInputError(message=error_message)

    if str_to_date(date_str=end_date_str) - str_to_date(date_str=start_date_str) > max_range:
        error_message = "Maximum date range is 93 calendar days."
        raise custom_exceptions.InvalidInputError(message=error_message)

    log.debug(msg="User input valid.")
    return selected_currency, start_date_str, end_date_str


def get_dates_to_check(start_date: datetime.date, days_difference: int) -> list[datetime.date]:
    """Create a list of dates to check for data in local database. Excludes weekends."""
    dates_to_check = []

    for i in range(days_difference):
        date_to_check = start_date + datetime.timedelta(days=i)

        if date_to_check.isoweekday() < 6:
            dates_to_check.append(date_to_check.strftime("%Y-%m-%d"))

    return dates_to_check


def get_difference_in_days(start_date: str, end_date: str) -> int:
    """Calculate difference in days between two dates."""
    return (str_to_date(date_str=end_date) - str_to_date(date_str=start_date)).days


def define_all_days_to_check(start_date: str, days_difference: int) -> list[str]:
    """Collect dates to check for data in local database. Excludes weekends."""
    days_to_check = []

    for i in range(days_difference):
        new_date = str_to_date(date_str=start_date) + datetime.timedelta(days=i)

        if new_date.isoweekday() < 6:
            days_to_check.append(new_date.strftime("%Y-%m-%d"))

    return days_to_check


def is_data_already_in_cache(data_present: list[str], start_date: str, end_date: str) -> bool:
    """Check if requested data is already in local database. If not, download from NBP API.

    Parameters:
        data_present (list[str]): list of dates in "YYYY-MM-DD" format representing data for a currency.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
    """

    days_difference = get_difference_in_days(start_date=start_date, end_date=end_date)

    days_to_check = define_all_days_to_check(start_date=start_date, days_difference=days_difference)

    for day in days_to_check:
        if day not in data_present:
            log.info(msg="Requested data not (fully) present in local DB, sending request to NBP API.")
            return False

    log.debug(msg="Requested data fully present in local db.")
    return True


def convert_nbp_api_list_to_sql_table_rows(currency_rates: dict, currency: str) -> list[tuple]:
    """Converts currency rates from NBP API to a list of tuples for insertion into the local database."""
    rows_to_insert = []

    for item in currency_rates["rates"]:
        effective_date = item["effectiveDate"]
        rate = item["mid"]
        rows_to_insert.append((effective_date, currency, rate))

    return rows_to_insert


@app.route(rule="/", methods=["GET", "POST"])
def index() -> str:
    """Main view for the app, fetches currency exchange rates from NBP API and displays them in a chart."""

    today, yesterday = config.today_and_yesterday()

    try:
        available_currencies = nbp_api_communication.fetch_available_currencies()

    except (custom_exceptions.NBPConnectionError, custom_exceptions.InvalidInputError) as e:
        return flask.render_template(
            template_name_or_list="index.html",
            error_message=e.message,
            chart_available=False,
            yesterday=yesterday,
        )

    if flask.request.method == "GET":
        return flask.render_template(
            template_name_or_list="index.html",
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )

    # POST request
    try:
        selected_currency, start_date, end_date = validate_user_input(
            request_form=flask.request.form, today=today, yesterday=yesterday
        )

        dates_recorded_for_currency = sqldb_communication.get_data_from_sql_table(
            currency=selected_currency,
            start_date=start_date,
            end_date=end_date,
            row_factory=lambda cursor, row: row[0],
        )

        data_already_in_cache = is_data_already_in_cache(
            data_present=dates_recorded_for_currency, start_date=start_date, end_date=end_date
        )

        if data_already_in_cache is False:
            currency_rates = nbp_api_communication.fetch_currency_rates(
                currency=selected_currency, start_date=start_date, end_date=end_date
            )
            rows_to_insert = convert_nbp_api_list_to_sql_table_rows(
                currency_rates=currency_rates, currency=selected_currency
            )
            sqldb_communication.save_currency_rates_to_db(rows_to_insert=rows_to_insert)

        currency_table = sqldb_communication.get_data_from_sql_table(
            currency=selected_currency, start_date=start_date, end_date=end_date
        )

        @flask.after_this_request
        def send_chart(response):
            plot.generate_chart(currency_table=currency_table, selected_currency=selected_currency)
            return response

        log.info(msg="Currency exchange rates fetched and chart generated successfully.")
        return flask.render_template(
            template_name_or_list="index.html",
            chart_available=True,
            available_currencies=available_currencies,
            selected_currency=selected_currency,
            yesterday=yesterday,
            start_date=start_date,
            end_date=end_date,
            currency_data=currency_table,
        )

    except (custom_exceptions.NBPConnectionError, custom_exceptions.InvalidInputError) as e:
        return flask.render_template(
            template_name_or_list="index.html",
            error_message=e.message,
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )

    except Exception as exc:  # pylint: disable=broad-except
        log.exception(msg=f"An unexpected error occurred:\n{exc}")
        return flask.render_template(
            template_name_or_list="index.html",
            error_message="An unexpected error occurred, please try again.",
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )


if __name__ == "__main__":
    log.info(msg="NBP currency exchange rates app started.")
    app.run()
