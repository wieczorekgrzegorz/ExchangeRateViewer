"""Configuration module for the exchange rate viewer application."""
import logging
import logging.config
import os
import yaml

import matplotlib

from exchange_rate_viewer.modules import sqldb_communication

log = logging.getLogger(name="app_logger")

NBP_RATES_URL = "https://api.nbp.pl/api/exchangerates/rates/a/"
NBP_TABLES_URL = "https://api.nbp.pl/api/exchangerates/tables/a"
DB_DIR_PATH = os.path.join("exchange_rate_viewer", "database")
DB_FILEPATH = os.path.join("exchange_rate_viewer", "database", "currency_rates.db")
LOGS_DIR_PATH = os.path.join("exchange_rate_viewer", "logs")
LOGS_FILEPATH = os.path.join("exchange_rate_viewer", "logs", "errors_log.log")
CHART_FILEPATH = os.path.join("exchange_rate_viewer", "static", "chart.png")
REQUEST_TIMEOUT = 60
LOGGING_CONFIG_FILEPATH = os.path.join("exchange_rate_viewer", "logging_config.yaml")
MAX_DATE_RANGE = 93  # Maximum range of days allowed by NBP API


def create_logs_dir() -> None:
    """Check if data folder exists and create it if not."""
    if not os.path.exists(path=LOGS_DIR_PATH):
        print(f"Creating logs directory in: {LOGS_DIR_PATH}")
        os.makedirs(name=LOGS_DIR_PATH)
        print(f"Logs directory created in: {LOGS_DIR_PATH}")
    else:
        print(f"Logs directory already exists in: {LOGS_DIR_PATH}, skipping creation.")


def create_logs_file() -> None:
    """Create database file if it doesn't exist."""
    if not os.path.exists(path=LOGS_FILEPATH):
        print(f"Creating logs file in: {LOGS_FILEPATH}")
        with open(file=LOGS_FILEPATH, mode="w+", encoding="utf-8") as file:
            file.write("")
        print(f"Logs file created in: {LOGS_FILEPATH}")
    else:
        print(f"Logs file already exists in: {LOGS_FILEPATH}, skipping creation.")


def setup_logging() -> None:
    """Set up logging configuration."""
    create_logs_dir()
    create_logs_file()
    with open(file=LOGGING_CONFIG_FILEPATH, mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(stream=f.read())
    logging.config.dictConfig(config=config)


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


def setup_app() -> None:
    """Set up the application."""
    create_data_dir()
    create_db_file()
    sqldb_communication.create_table()

    set_matplotlib_backend()

    log.info(msg="Application setup completed.")
