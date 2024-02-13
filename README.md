# NBP currency Flask app

## Description
This is a Python Flask application designed for Python developers. It fetches currency exchange rates from the NBP API, saves them to an SQLite database, and generates a chart for a selected currency. It provides a practical example of integrating APIs, working with databases, and generating visualizations.

## Instruction

- To run this application locally, you need to install Flask and other required libraries.
- Use "pip install -r requirements.txt" to install the dependencies listed in the requirements.txt file.
- Then, run the "python app.py" command in your terminal or command prompt from the project directory to start the server.
- Finally, open your web browser and go to http://localhost:5000/ to access the application.

## How it works
Here's an explanation of the application's components:

- Import necessary libraries: The required libraries, including Flask for web development, are imported.
- Define constants: Constants are defined for the data and static folders and the database file path.
- Create a list of available currencies: The application fetches currency data from the NBP API and creates a sorted list of available currencies.
- Define functions:
    - fetch_currency_rates(): Fetches currency exchange rates from the NBP API for a specified currency and date range.
    - save_currency_rates_to_db(): Saves the fetched exchange rate information to an SQLite database.
    - get_currency_data(): Retrieves currency data from the SQLite database based on the selected currency and date range.
    - generate_chart(): Generates a chart using matplotlib for the selected currency and date range.
- Define the main route: The main route '/' is defined using Flask's @app.route decorator. It handles both GET and POST requests.
    - GET request: Renders the index.html template without a chart but with available currencies.
    - POST request: Validates the input dates (max period 93 days as per API NBP, 'end date' can't be earlier than 'start date', neither date can be later than yesterday), fetches the currency rates, saves them to the database, generates a chart, and renders the index.html template with the chart and available currencies.


## Development Environment

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
