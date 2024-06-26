# NBP currency Flask app, conteinarized (with Docker)

## Description
This is a Python Flask application designed for Python developers. It fetches currency exchange rates from the NBP API, saves them to an SQLite database, and generates a chart for a selected currency. It provides a practical example of integrating APIs, working with databases, and generating visualizations.

## Features

- Creating a RESTful API using `Flask`
- Fetching currency exchange rates from the NBP API using `requests` module
- Saving exchange rates to an SQLite database using `sqlite3`
- Generating a chart for a selected currency using `matplotlib`
- Using environment variables to store sensitive data
- Using `pre-commit` hooks to ensure code quality and consistency
- Using `Poetry` for dependency management
- Using `Docker` to containerize the application
- Using `GitHub Actions` for continuous integration
- using `yaml` for logging configuration


## Running the Application

This app is containerized using Docker. To run the application, you need to have Docker installed on your machine. You can install Docker by following the instructions on the [official website](https://docs.docker.com/get-docker/).

Before building a Docker image, you need to create a `.env` file inside the `.docker` directory and set the following environment variables:
```
DB_FILEPATH=exchange_rate_viewer/database/currency_rates.db
LOGS_FILEPATH=exchange_rate_viewer/logs/warnings_errors_log.jsonl
CHART_FILEPATH=exchange_rate_viewer/static/chart.png
LOGGING_CONFIG_FILEPATH=exchange_rate_viewer/logging_config.yaml
```


Once you have Docker installed and .env file prepared, you can run the application using the following command in .docker directory:

```bash
docker-compose up --build
```

Once the application is running, you can access it by visiting `http://localhost:5000` in your web browser.

## Development Environment

### Testing

This project uses `unittest` for testing. You can run the tests using the following command:

```bash
poetry run python -m unittest
```

### Logging

This project uses the `logging` module to log warnings and errors to a JSON Lines file. The logging configuration is stored in the `logging_config.yaml` file. You can change the logging configuration by modifying this file.

### Pre-commit Hooks

This repository uses pre-commit hooks to ensure code quality and consistency. Pre-commit hooks are scripts that run automatically before each commit to check for any errors or issues.

#### Installation and Usage

To use the pre-commit hooks in this repository, you need to have the `pre-commit` package installed. For detailed instruction please refer to [the official documentation](https://python-poetry.org/docs/#installation).
You can install it using pip:

```bash
pip install pre-commit
```

Once the `pre-commit` package is installed, you can set up the pre-commit hooks for this repository by running:

```bash
pre-commit install
```

Now, the pre-commit hooks will automatically run before each commit. If any issues are found, the commit will be aborted, and you will be given a report of the issues.

Remember, you can manually run all pre-commit hooks on your repository without making a commit by using:

```bash
pre-commit run --all-files
```


### Dependencies Management: Poetry

This project uses Poetry for dependency management. Poetry is a tool for Python that helps in handling library dependencies.

#### Installation and Usage

To manage dependencies, you need to have `poetry` installed.

**WATCHOUT!** Poetry should always be installed in a dedicated virtual environment to isolate it from the rest of your system.

You can install it using pip:

```bash
pip install poetry
```

Once `poetry` is installed, you can install the project dependencies by running:

```bash
poetry install
```

This command reads the pyproject.toml file from the current directory, resolves the dependencies, and installs them.

If you want to add a new dependency to the project, you can do so by running:

```bash
poetry add <package-name>
```

To remove a dependency, you can use:

```bash
poetry remove <package-name>
```

#### Poetry Pre-commit Hooks

Remember, to ensure that the hooks are using the same dependencies as your poetry environment, you can add the following to your .pre-commit-config.yaml:

```yaml
  - repo: https://github.com/python-poetry/poetry
    rev: v1.7.1
    hooks:
      - id: poetry-check
      - id: poetry-lock
      - id: poetry-export
        args: ["-f", "requirements.txt", "-o", "requirements.txt"]
      - id: poetry-install
```

The `poetry-check` hook calls the `poetry check` command to make sure the poetry configuration does not get committed in a broken state.

The `poetry-lock` hook calls the `poetry lock` command to make sure the lock file is up-to-date when committing changes.

The `poetry-export` hook calls the `poetry export` command to sync your `requirements.txt` file with your current dependencies.

The `poetry-install` hook calls the `poetry install` command to make sure all locked packages are installed.

For more into on `poetry pre-commit hooks`, please refer to the [official documentation](https://python-poetry.org/docs/master/pre-commit-hooks/).
