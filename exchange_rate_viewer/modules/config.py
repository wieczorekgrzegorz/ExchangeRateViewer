"""Configuration module for the exchange rate viewer application."""
import datetime
import logging
from logging.config import dictConfig
import os
import yaml

import matplotlib

from exchange_rate_viewer.modules import sqldb_communication

log = logging.getLogger(name="log")

NBP_RATES_URL = "https://api.nbp.pl/api/exchangerates/rates/a/"
NBP_TABLES_URL = "https://api.nbp.pl/api/exchangerates/tables/a"
DB_DIR_PATH = os.path.join("src", "database")
DB_FILEPATH = os.path.join("exchange_rate_viewer", "database", "currency_rates.db")
CHART_FILEPATH = os.path.join("exchange_rate_viewer", "static", "chart.png")
REQUEST_TIMEOUT = 60
LOGGING_CONFIG_FILEPATH = os.path.join("exchange_rate_viewer", "logging_config.yaml")
MAX_DATE_RANGE = 93  # Maximum range of days allowed by NBP API


def today_and_yesterday() -> tuple[datetime.date, datetime.date]:
    """Return today's and yesterday's date."""
    return datetime.datetime.now().date(), datetime.datetime.now().date() - datetime.timedelta(days=1)


def setup_logging() -> None:
    """Set up logging configuration."""
    with open(file=LOGGING_CONFIG_FILEPATH, mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(stream=f.read())
    dictConfig(config=config)


def create_data_dir() -> None:
    """Check if data folder exists and create it if not."""
    if not os.path.exists(path=DB_DIR_PATH):
        log.debug(msg="Creating data directory.")
        os.makedirs(name=DB_DIR_PATH)
        log.debug(msg=f"Data directory created in: {DB_DIR_PATH}")
    else:
        log.debug(msg="Data directory already exists, skipping creation.")


def create_db_file() -> None:
    """Create database file if it doesn't exist."""
    if not os.path.exists(path=DB_FILEPATH):
        log.debug(msg="Creating database file.")
        with open(file=DB_FILEPATH, mode="w+", encoding="utf-8") as file:
            file.write("")
        log.debug(msg=f"Database file created in: {DB_FILEPATH}")
    else:
        log.debug(msg="Database file already exists, skipping creation.")


def set_matplotlib_backend() -> None:
    """Set a non-reactive backend for matplotlib to avoid
    "Tcl_AsyncDelete: async handler deleted by the wrong thread" error."""
    matplotlib.use(backend="Agg")


def setup() -> None:
    """Set up the application."""

    setup_logging()
    log.info(msg="NBP currency exchange rates app started.")

    create_data_dir()
    create_db_file()
    sqldb_communication.create_table()

    set_matplotlib_backend()
    log.info(msg="Application setup complete.")
