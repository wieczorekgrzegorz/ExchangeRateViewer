"""Module for communication with the local SQLite database."""

import datetime
import logging

import sqlite3

from modules import config

log = logging.getLogger(name="app_logger")


def create_sql_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    return sqlite3.connect(database=config.DB_FILEPATH)


def create_table() -> None:
    """Create a table in the database."""
    log.debug(msg="Creating table 'rates' in the database (if it doesn't exist).")
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
        log.debug(msg=f"Executing query: {query}.")
        conn_cursor.execute(query)

    log.debug(msg="'CREATE TABLE IF NOT EXISTS' query executed successfully.")


def get_data_from_sql_table(
    currency: str,
    start_date: datetime.date,
    end_date: datetime.date,
) -> list[tuple[str, float]]:
    """Fetches currency exchange rates from local database.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (datetime.date): start date in "YYYY-MM-DD" format.
        end_date (datetime.date): end date in "YYYY-MM-DD" format.
    """
    log.info(msg=f"Fetching currency exchange rates from local DB ({currency}/PLN, {start_date}, {end_date}).")
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
        log.debug(msg=f"Executing query: {query} with parameters: {currency}, {start_date}, {end_date}.")
        c.execute(query, (currency, start_date, end_date))

        currency_table = c.fetchall()

        log.debug(msg=f"Local SQL table read successfully: {currency_table}")

        log.info(msg="Local SQL table read successfully.")

        return currency_table


def save_currency_rates_to_db(rows_to_insert: list[tuple]) -> None:
    """Saves currency exchange rates to local database."""
    log.info(msg="Saving currency exchange rates to local DB.")
    conn = create_sql_connection()
    with conn:
        c = conn.cursor()

        query = """INSERT OR REPLACE INTO rates VALUES (?, ?, ?)"""

        log.debug(msg="Executing query: 'INSERT OR REPLACE INTO rates VALUES (?, ?, ?)' with multiple rows to insert.")

        c.executemany(query, rows_to_insert)

        log.info(msg="Currency exchange rates saved to local DB successfully.")
