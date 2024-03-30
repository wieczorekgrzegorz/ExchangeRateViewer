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
