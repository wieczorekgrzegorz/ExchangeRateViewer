"""Set of custom exceptions for the application."""
import logging

log = logging.getLogger(name="log." + __name__)


class InvalidInputError(Exception):
    """Exception raised for invalid user input."""

    def __init__(self, message) -> None:
        self.message = message
        log.exception(msg=f"InvalidInputError:\n{self.message}")

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"InvalidInputError(message={self.message})"


class NBPConnectionError(Exception):
    """Exception raised for connection error with NBP API."""

    def __init__(self, message) -> None:
        self.message = message
        log.exception(msg=f"NBPConnectionError:\n{self.message}")

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"ConnectionError(message={self.message})"
