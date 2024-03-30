"""Configuration module for the exchange rate viewer application."""

import logging
import logging.config
import os
import yaml

log = logging.getLogger(name="app_logger")

DB_FILEPATH = os.environ["DB_FILEPATH"]
LOGS_FILEPATH = os.environ["LOGS_FILEPATH"]
CHART_FILEPATH = os.environ["CHART_FILEPATH"]
LOGGING_CONFIG_FILEPATH = os.environ["LOGGING_CONFIG_FILEPATH"]

NBP_RATES_URL = "https://api.nbp.pl/api/exchangerates/rates/a/"
NBP_TABLES_URL = "https://api.nbp.pl/api/exchangerates/tables/a"

MAX_DATE_RANGE = 93  # Maximum range of days allowed by NBP API
REQUEST_TIMEOUT = 60


def load_logging_config() -> dict:
    """Load logging configuration from a file."""
    with open(file=LOGGING_CONFIG_FILEPATH, mode="r", encoding="utf-8") as f:
        config = yaml.safe_load(stream=f.read())

    return config


def replace_log_filepath(config: dict) -> None:
    """Replace ${LOGS_FILEPATH} in the logging config."""
    for handler in config["handlers"].values():
        if "filename" in handler and "${LOGS_FILEPATH}" in handler["filename"]:
            handler["filename"] = os.getenv(key="LOGS_FILEPATH")


def setup_logging() -> None:
    """Set up logging configuration."""
    config = load_logging_config()

    replace_log_filepath(config=config)

    logging.config.dictConfig(config=config)
    log.info(msg="NBP currency exchange rates app started.")

    log.info(msg="Logging configuration set up successfully.")
