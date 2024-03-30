"""Set of custom exceptions for the application."""
import logging

import requests

log = logging.getLogger(name="app_logger")


class InvalidInputError(Exception):
    """Exception raised for invalid user input."""

    def __init__(self, message) -> None:
        self.message = message
        log.warning(msg=f"InvalidInputError:\n{self.message}", stacklevel=2)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"InvalidInputError(message={self.message})"


class NBPConnectionError(Exception):
    """Exception raised for connection error with NBP API."""

    def __init__(self, message, response: requests.Response) -> None:
        self.message = message
        log.exception(
            msg=f"NBPConnectionError: {self.message}", stacklevel=2, extra=self.build_extra_details(response=response)
        )

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"NBPConnectionError(message={self.message})"

    def build_extra_details(self, response: requests.Response) -> dict:
        """Build extra details for the log record from the response."""
        try:
            response_content = response.content.decode(encoding="utf-8-sig")
        except UnicodeDecodeError:
            response_content = response.content.decode(encoding="utf-8-sig", errors="replace")

        extra = {
            "response_status_code": response.status_code,
            "response_reason": response.reason,
            "response_content": response_content,
        }
        log.debug(msg=f"Extra details: {extra}")
        return extra
