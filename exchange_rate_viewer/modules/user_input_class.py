"""Module for user input validation and handling."""

import datetime
import logging

from werkzeug.datastructures import ImmutableMultiDict

from modules import custom_exceptions, datetime_operations

log = logging.getLogger(name="app_logger")


class UserInput:
    """Class for user input validation and handling.

    Attributes:
        request_form (ImmutableMultiDict[str, str]): Form data from the request.
        today (datetime.date): Today's date.
        yesterday (datetime.date): Yesterday's date.
        selected_currency (str | None): Selected currency from the form.
        start_date (datetime.date): Start date from the form.
        end_date (datetime.date): End date from the form.
        start_date_str (str): Start date from the form as a string.
        end_date_str (str): End date from the form as a string.

    Raises:
        custom_exceptions.InvalidInputError: If any of the required fields are not selected.
    """

    def __init__(self, request_form: ImmutableMultiDict[str, str]) -> None:
        self.selected_currency = self.get_obj_from_request_form(request_form=request_form, object_name="currency")
        self.start_date_str = self.get_obj_from_request_form(request_form=request_form, object_name="start_date")
        self.end_date_str = self.get_obj_from_request_form(request_form=request_form, object_name="end_date")
        self.start_date = self.convert_string_to_date(string=self.start_date_str)
        self.end_date = self.convert_string_to_date(string=self.end_date_str)

    def get_obj_from_request_form(self, request_form: dict[str, str], object_name: str) -> str:
        """Returns the object from the form."""
        try:
            return request_form[object_name]
        except KeyError as exc:
            error_message = f"Please select {object_name}."
            raise custom_exceptions.InvalidInputError(message=error_message) from exc

    def convert_string_to_date(self, string: str) -> datetime.date:
        """Returns the end date from the form."""
        return datetime_operations.str_to_date(date_str=string)


class Validator:
    """Class for user input validation.

    Parameters:
        user_input (UserInput): User input object.

    Attributes:
        user_input (UserInput): User input object.
        max_range (datetime.timedelta): Maximum date range allowed by NBP API.
    """

    def __init__(self, user_input: UserInput) -> None:
        self.user_input = user_input
        self.max_range = datetime_operations.get_max_date_range()

    def run(self) -> None:
        """Validates the user input. Raises custom_exceptions.InvalidInputError if invalid."""
        self.validate_currency()
        self.validate_start_date()
        self.validate_date_range()

    def validate_currency(self) -> None:
        """Validates the selected currency. Raises an exception if not selected."""
        if not self.user_input.selected_currency:
            error_message = "Please select a currency."
            raise custom_exceptions.InvalidInputError(message=error_message)

    def validate_start_date(self) -> None:
        """Validates the start date. Raises an exception if invalid."""
        if datetime_operations.start_date_after_end_date(
            start_date=self.user_input.start_date_str, end_date=self.user_input.end_date_str
        ):
            error_message = "'Start Date' cannot be after 'End Date'."
            raise custom_exceptions.InvalidInputError(message=error_message)

    def validate_date_range(self) -> None:
        """Validates the date range. Raises an exception if invalid."""
        if datetime_operations.max_range_exceeded(
            start_date=self.user_input.start_date_str, end_date=self.user_input.end_date_str, max_range=self.max_range
        ):
            error_message = "Maximum date range is 93 calendar days."
            raise custom_exceptions.InvalidInputError(message=error_message)


def validate(
    request_form: ImmutableMultiDict[str, str], today: datetime.date, yesterday: datetime.date
) -> tuple[str, str, str]:
    """Validates user input from the form.

    Raises:
        custom_exceptions.InvalidInputError: If input is invalid.
    """
    error_message = None
    max_range = datetime_operations.get_max_date_range()

    selected_currency = request_form.get(key="currency")

    if not selected_currency:
        error_message = "Please select a currency."
        raise custom_exceptions.InvalidInputError(message=error_message)

    start_date_str = request_form.get(key="start_date", default=datetime_operations.date_to_str(date_obj=yesterday))
    end_date_str = request_form.get(key="end_date", default=datetime_operations.date_to_str(date_obj=today))

    if datetime_operations.start_date_after_end_date(start_date=start_date_str, end_date=end_date_str):
        error_message = "'Start Date' cannot be after 'End Date'."
        raise custom_exceptions.InvalidInputError(message=error_message)

    if datetime_operations.max_range_exceeded(start_date=start_date_str, end_date=end_date_str, max_range=max_range):
        error_message = "Maximum date range is 93 calendar days."
        raise custom_exceptions.InvalidInputError(message=error_message)

    log.debug(msg="User input valid.")
    return selected_currency, start_date_str, end_date_str
