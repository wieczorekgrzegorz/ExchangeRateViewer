"""Module for user input validation and handling."""

import logging


from modules import custom_exceptions, datetime_operations, user_input_class

log = logging.getLogger(name="app_logger")


class InputValidator:
    """Class for user input validation.

    Parameters:
        user_input (user_input_class.UserInput): User input object.

    Attributes:
        user_input (user_input_class.UserInput): User input object.
        max_range (datetime.timedelta): Maximum date range allowed by NBP API.
    """

    def __init__(self, user_input: user_input_class.UserInput) -> None:
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
