"""Flask app for fetching and displaying currency exchange rates from NBP API."""
import logging
import datetime
import sqlite3

import flask
from werkzeug.datastructures import ImmutableMultiDict

from modules import custom_exceptions, config, nbp_api_communication, plot

log = logging.getLogger(name="log." + __name__)
config.setup()


app = flask.Flask(import_name=__name__)


def str_to_date(date_str: str) -> datetime.date:
    """Convert date string to datetime object."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def date_to_str(date_obj: datetime.date) -> str:
    """Convert date object to string."""
    return date_obj.strftime("%Y-%m-%d")


def get_difference_in_days(start_date: datetime.date, end_date: datetime.date) -> int:
    """Calculate difference in days between two dates."""
    return (end_date - start_date).days


def is_data_already_in_cache(currency: str, start_date: datetime.date, end_date: datetime.date) -> bool:
    """Check if requested data is already in local database. If not, download from NBP API.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
    """

    days_difference = get_difference_in_days(start_date=start_date, end_date=end_date)

    dates_to_check = []

    for i in range(days_difference):
        date_to_check = start_date + datetime.timedelta(days=i)

        # Weekends excluded as there's no exchange on weekends.
        if date_to_check.isoweekday() < 6:
            dates_to_check.append(date_to_check.strftime("%Y-%m-%d"))

    conn = sqlite3.connect(database=config.DB_FILEPATH)
    conn.row_factory = lambda cursor, row: row[0]
    cached_list = []

    with conn:
        c = conn.cursor()
        query = """
                    SELECT
                        date,
                        rate
                    FROM
                        rates
                    WHERE
                        currency = ? AND date BETWEEN ? AND ?
                    ORDER BY
                        date
                """
        try:
            c.execute(query, (currency, start_date, end_date))
        except sqlite3.OperationalError:
            return False

    cached_list = c.fetchall()

    for day in dates_to_check:
        if day not in cached_list:
            log.debug("Requested data not in cache, downloading from NBP API.")
            return False
    log.debug("Requested data aready in local db.")
    return True


def create_table(conn_cursor: sqlite3.Cursor) -> None:
    """Create a table in the database."""
    query = """
            CREATE TABLE IF NOT EXISTS rates(
                date     TIMESTAMP NOT NULL,
                currency TEXT NOT NULL,
                rate     REAL NOT NULL
            )
            """
    conn_cursor.execute(query)


def create_rows_to_insert(currency_rates: dict, currency: str) -> list[tuple]:
    """Create rows to insert into the database."""
    rows_to_insert = []

    for item in currency_rates["rates"]:
        effective_date = item["effectiveDate"]
        rate = item["mid"]
        rows_to_insert.append((effective_date, currency, rate))

    return rows_to_insert


def save_currency_rates_to_db(rows_to_insert: list[tuple]) -> None:
    """Saves currency exchange rates to local database."""
    log.debug(msg="Saving currency exchange rates to local DB.")
    conn = sqlite3.connect(database=config.DB_FILEPATH)
    with conn:
        c = conn.cursor()
        create_table(conn_cursor=c)

        c.executemany("INSERT INTO rates VALUES (?, ?, ?)", rows_to_insert)

        # remove duplicated rows
        c.execute(
            """
                    DELETE
                    FROM rates AS r1
                    WHERE EXISTS (
                        SELECT *
                        FROM rates AS r2
                        WHERE r1.date = r2.date
                            AND r1.currency = r2.currency
                            AND r1.rowid > r2.rowid
                            )
                        """
        )

        log.debug(msg="Currency exchange rates saved to local DB successfully.")


def get_data_from_local_db(currency: str, start_date_str: str, end_date_str: str) -> list[tuple]:
    """Fetches currency exchange rates from local database.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
    """
    log.debug(msg=f"Fetching currency exchange rates from local DB ({currency}, {start_date_str}, {end_date_str}).")
    conn = sqlite3.connect(database=config.DB_FILEPATH)

    with conn:
        c = conn.cursor()
        query = """
            SELECT
                date,
                rate
            FROM
                rates
            WHERE
                currency = ?
                AND date BETWEEN ? AND ?
            ORDER BY
                date
        """
        c.execute(query, (currency, start_date_str, end_date_str))

        log.debug(msg="Currency exchange rates fetched successfully.")

        return c.fetchall()


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

        # Weekends excluded as there's no exchange on weekends.
        if date_to_check.isoweekday() < 6:
            dates_to_check.append(date_to_check.strftime("%Y-%m-%d"))

    return dates_to_check


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
        selected_currency, start_date_str, end_date_str = validate_user_input(
            request_form=flask.request.form, today=today, yesterday=yesterday
        )

        start_date = str_to_date(date_str=start_date_str)
        end_date = str_to_date(date_str=end_date_str)

        data_already_in_cache = is_data_already_in_cache(
            currency=selected_currency, start_date=start_date, end_date=end_date
        )

        if data_already_in_cache is False:
            currency_rates = nbp_api_communication.fetch_currency_rates(
                currency=selected_currency, start_date_str=start_date_str, end_date_str=end_date_str
            )
            rows_to_insert = create_rows_to_insert(currency_rates=currency_rates, currency=selected_currency)
            save_currency_rates_to_db(rows_to_insert=rows_to_insert)

        currency_table = get_data_from_local_db(
            currency=selected_currency, start_date_str=start_date_str, end_date_str=end_date_str
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
