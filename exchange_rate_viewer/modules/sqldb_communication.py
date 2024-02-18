"""Module for communication with the local SQLite database."""
import datetime
import logging

import sqlite3

from modules import config

log = logging.getLogger(name="log." + __name__)


def create_sql_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    return sqlite3.connect(database=config.DB_FILEPATH)


def create_table() -> None:
    """Create a table in the database."""
    log.debug(msg="Creating table 'rates' in the database.")
    conn = create_sql_connection()
    with conn:
        conn_cursor = conn.cursor()
        query = """
                CREATE TABLE IF NOT EXISTS rates(
                    date     TIMESTAMP NOT NULL,
                    currency TEXT NOT NULL,
                    rate     REAL NOT NULL,
                    UNIQUE(date, currency)
                )
                """
        conn_cursor.execute(query)

    log.debug(msg="Table 'rates' created in the database.")


def get_data_from_sql_table(currency: str, start_date_str: str, end_date_str: str) -> list[tuple]:
    """Fetches currency exchange rates from local database.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
    """
    log.debug(msg=f"Fetching currency exchange rates from local DB ({currency}, {start_date_str}, {end_date_str}).")
    conn = create_sql_connection()

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


def save_currency_rates_to_db(rows_to_insert: list[tuple]) -> None:
    """Saves currency exchange rates to local database."""
    log.debug(msg="Saving currency exchange rates to local DB.")
    conn = create_sql_connection()
    with conn:
        c = conn.cursor()

        c.executemany(
            "INSERT OR REPLACE INTO rates VALUES (?, ?, ?)",
            rows_to_insert,
        )

        log.debug(msg="Currency exchange rates saved to local DB successfully.")


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

        if date_to_check.isoweekday() < 6:
            dates_to_check.append(date_to_check.strftime("%Y-%m-%d"))

    conn = create_sql_connection()
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
