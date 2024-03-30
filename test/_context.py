import os

os.chdir(path="exchange_rate_viewer")
print("context CWD: ", os.getcwd())


mock_env_vars = {
    "DB_FILEPATH": "mock_db.sqlite",
    "LOGS_FILEPATH": "mock_logs.log",
    "CHART_FILEPATH": "mock_chart.png",
    "LOGGING_CONFIG_FILEPATH": "logging_config.yaml",
}
