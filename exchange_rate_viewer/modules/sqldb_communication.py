"""Module for communication with the local SQLite database."""
import logging

import sqlite3
from typing import Callable, Optional

from modules import config

log = logging.getLogger(name="log." + __name__)


def create_sql_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    return sqlite3.connect(database=config.DB_FILEPATH)


def create_table() -> None:
    """Create a table in the database."""
    log.info(msg="Creating table 'rates' in the database.")
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

    log.info(msg="Table 'rates' created in the database.")


def get_data_from_sql_table(
    currency: str,
    start_date: str,
    end_date: str,
    row_factory: Optional[sqlite3.Row | Callable] = None,
) -> list:
    """Fetches currency exchange rates from local database.

    Parameters:
        currency (str): currency code as per NBP API.
        start_date (str): start date in "YYYY-MM-DD" format.
        end_date (str): end date in "YYYY-MM-DD" format.
        row_factory (sqlite3.Row | Callable): row factory for the cursor.
    """
    log.debug(msg=f"Fetching currency exchange rates from local DB ({currency}, {start_date}, {end_date}).")
    conn = create_sql_connection()

    if row_factory:
        conn.row_factory = row_factory

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
        c.execute(query, (currency, start_date, end_date))

        currency_table = c.fetchall()

        log.debug(msg=f"Local SQL table read successfully: {currency_table}")

        log.info(msg="Local SQL table read successfully.")

        return currency_table


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
