"""Configuration module for the exchange rate viewer application."""
import datetime
import logging
from logging.config import dictConfig

import os


import matplotlib

log = logging.getLogger(name="__main__." + __name__)


NBP_RATES_URL = "https://api.nbp.pl/api/exchangerates/rates/a/"
NBP_TABLES_URL = "https://api.nbp.pl/api/exchangerates/tables/a"
DB_FILEPATH = os.path.join("exchange_rate_viewer", "database", "currency_rates.db")
CHART_FILE = os.path.join("exchange_rate_viewer", "static", "chart.png")
REQUEST_TIMEOUT = 60
LOGGING_LEVEL = "DEBUG"
LOG_DIR = os.path.join("exchange_rate_viewer", "logs")
LOG_FILENAME = os.path.join(LOG_DIR, "logs.log")


def today_and_yesterday() -> tuple[datetime.date, datetime.date]:
    """Return today's and yesterday's date."""
    return datetime.datetime.now().date(), datetime.datetime.now().date() - datetime.timedelta(days=1)


def create_log_dir() -> None:
    """Create a folder for logs if it doesn't exist."""
    if not os.path.exists(path=LOG_DIR):
        os.makedirs(name=LOG_DIR)


def setup_logger() -> None:
    """Set up the logger."""

    # https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
    # log.setLevel(level=LOGGING_LEVEL)
    # formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")
    # create_log_dir()

    # file_handler = logging.FileHandler(filename=LOG_FILENAME, mode="a", encoding="utf-8")
    # file_handler.setLevel(level=logging.DEBUG)
    # file_handler.setFormatter(fmt=formatter)
    # log.addHandler(hdlr=file_handler)
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": LOGGING_LEVEL, "handlers": ["wsgi"]},
        }
    )


def create_data_dir() -> None:
    """Check if data folder exists and create it if not."""
    if not os.path.exists(path=os.path.join("src", "database")):
        os.makedirs(name=os.path.join("src", "database"))


def create_db_file() -> None:
    """Create database file if it doesn't exist."""
    if not os.path.exists(path=DB_FILEPATH):
        with open(file=DB_FILEPATH, mode="w+", encoding="utf-8") as file:
            file.write("")


def set_matplotlib_backend() -> None:
    """Set a non-reactive backend for matplotlib to avoid
    "Tcl_AsyncDelete: async handler deleted by the wrong thread" error."""
    matplotlib.use(backend="Agg")


def setup() -> None:
    """Set up the application."""

    setup_logger()
    create_data_dir()
    create_db_file()
    set_matplotlib_backend()
    log.debug(msg="Application setup complete.")
