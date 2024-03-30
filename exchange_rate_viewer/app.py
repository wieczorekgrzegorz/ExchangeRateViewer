"""Flask app for fetching and displaying currency exchange rates from NBP API."""

import datetime
import logging

import flask

from modules import (
    custom_exceptions,
    config,
    datetime_operations,
    input_validator_class,
    nbp_api_communication,
    plot,
    sqldb_communication,
    user_input_class,
)

log = logging.getLogger(name="app_logger")


app = flask.Flask(import_name=__name__)


def data_already_in_cache(
    currency_table: list[tuple[str, float]],
    days_to_check: list[datetime.date],
) -> bool:
    """Check if requested data is already in local database. If not, download from NBP API.

    Parameters:
        data_present (list[str]): list of dates in "YYYY-MM-DD" format representing data for a currency.
        days_to_check (list[datetime.date]): list of dates to check.
    """
    if not currency_table:
        log.info(msg="Requested data not present in local DB, sending request to NBP API.")
        return False

    for day in days_to_check:
        if day not in currency_table:
            log.info(msg="Requested data not (fully) present in local DB, sending request to NBP API.")
            return False

    log.info(msg="Requested data fully present in local db. Fetching from local db.")
    return True


def download_from_nbp_api(user_input: user_input_class.UserInput) -> list[tuple[str, float]]:
    """Download currency exchange rates from NBP API and save them to local database.
    Returns the data from the local database.
    """
    log.info(msg="Data not fully present in local database, fetching from NBP API.")
    sqldb_communication.save_currency_rates_to_db(
        rows_to_insert=nbp_api_communication.fetch_currency_rates(
            currency=user_input.selected_currency,
            start_date=user_input.start_date,
            end_date=user_input.end_date,
        )
    )

    return sqldb_communication.get_data_from_sql_table(
        currency=user_input.selected_currency, start_date=user_input.start_date, end_date=user_input.end_date
    )


@app.route(rule="/", methods=["GET", "POST"])
def index() -> str:
    """Main view for the app, fetches currency exchange rates from NBP API and displays them in a chart."""

    yesterday = datetime_operations.yesterday()

    try:
        available_currencies = nbp_api_communication.fetch_available_currencies()

    except (custom_exceptions.NBPConnectionError, custom_exceptions.InvalidInputError) as e:
        return flask.render_template(
            template_name_or_list="index.html",
            error_message=e.message,
            chart_available=False,
            yesterday=yesterday,
        )

    if flask.request.method == "GET":
        return flask.render_template(
            template_name_or_list="index.html",
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )

    # else: flask.request.method == "POST"
    try:
        user_input = user_input_class.UserInput(request_form=flask.request.form)
        validator = input_validator_class.InputValidator(user_input=user_input)
        validator.run()

    except custom_exceptions.InvalidInputError as e:
        return flask.render_template(
            template_name_or_list="index.html",
            error_message=e.message,
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )

    try:
        log.info(
            msg=f"Checking if data for pair {user_input.selected_currency}/PLN for dates {user_input.start_date} to {user_input.end_date} is already present in local database."  # pylint: disable=line-too-long
        )
        currency_table = sqldb_communication.get_data_from_sql_table(
            currency=user_input.selected_currency,
            start_date=user_input.start_date,
            end_date=user_input.end_date,
        )

        if not data_already_in_cache(
            currency_table=currency_table,
            days_to_check=datetime_operations.define_all_days_to_check(
                start_date=user_input.start_date,
                days_difference=datetime_operations.get_difference_in_days(
                    start_date=user_input.start_date,
                    end_date=user_input.end_date,
                ),
            ),
        ):
            currency_table = download_from_nbp_api(user_input=user_input)

        @flask.after_this_request
        def send_chart(response):
            plot.generate_chart(currency_table=currency_table, selected_currency=user_input.selected_currency)
            return response

        log.info(msg="NBP currency exchange rates app finished successfully.")
        return flask.render_template(
            template_name_or_list="index.html",
            chart_available=True,
            available_currencies=available_currencies,
            selected_currency=user_input.selected_currency,
            yesterday=yesterday,
            start_date=user_input.start_date,
            end_date=user_input.end_date,
            currency_data=currency_table,
        )

    except custom_exceptions.NBPConnectionError as e:
        return flask.render_template(
            template_name_or_list="index.html",
            error_message=e.message,
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )

    except Exception as exc:  # pylint: disable=broad-except
        log.exception(msg=f"An unexpected error occurred:\n{exc}", stacklevel=2)
        return flask.render_template(
            template_name_or_list="index.html",
            error_message="An unexpected error occurred, please try again.",
            chart_available=False,
            available_currencies=available_currencies,
            yesterday=yesterday,
        )


if __name__ == "__main__":
    config.setup()
    log.info(msg="NBP currency exchange rates app started.")

    app.run(host="0.0.0.0", port=5000)
