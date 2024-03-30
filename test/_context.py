"""Context for tests. It sets the path to the main module and environment variables for tests."""

import pathlib
import sys

path = pathlib.Path(__file__).parents[1].joinpath("exchange_rate_viewer")

sys.path.append(str(object=path))

mock_env_vars = {
    "DB_FILEPATH": "mock_db.sqlite",
    "LOGS_FILEPATH": "mock_logs.log",
    "CHART_FILEPATH": "mock_chart.png",
    "LOGGING_CONFIG_FILEPATH": "logging_config.yaml",
}
