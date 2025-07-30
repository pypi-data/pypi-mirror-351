import json
import traceback

from darca_log_facility.logger import DarcaLogger


class DarcaException(Exception):
    """
    A powerful and generic base exception class providing structured details,
    logging via DarcaLogger, and serialization.
    """

    def __init__(self, message, error_code=None, metadata=None, cause=None):
        """
        Initialize a DarcaException with detailed information.

        :param message: Error message (str)
        :param error_code: Custom error code (int or str, optional)
        :param metadata: Additional metadata (dict, optional)
        :param cause: The original exception that caused this error (optional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.metadata = metadata or {}
        self.cause = cause

        # Log the exception
        self.log_exception()

    def log_exception(self):
        """
        Logs the exception details using DarcaLogger.
        Always logs as an error because exceptions indicate failure.
        """
        logger = DarcaLogger("darca-exception").get_logger()

        # Ensure the logger is part of Python's default logging system
        if not logger.handlers:
            import logging

            logger.addHandler(logging.StreamHandler())

        log_entry = {
            "error_code": self.error_code,
            "message": self.message,
            "metadata": self.metadata,
            "cause": str(self.cause) if self.cause else None,
            "stack_trace": traceback.format_exc(),
        }

        logger.error(
            json.dumps(log_entry)
        )  # Ensure Python logging captures this

    def to_dict(self):
        """
        Convert exception details to a dictionary.

        :return: Dictionary representation of the exception
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "metadata": self.metadata,
            "cause": str(self.cause) if self.cause else None,
            "stack_trace": traceback.format_exc(),
        }

    def __str__(self):
        """
        String representation of the exception.
        """
        cause_msg = f", caused by {self.cause}" if self.cause else ""
        return f"[{self.error_code}] {self.message}{cause_msg}"

    def __repr__(self):
        """
        Official string representation.
        """
        return (
            f"DarcaException(error_code={self.error_code}, "
            f"message={self.message})"
        )
