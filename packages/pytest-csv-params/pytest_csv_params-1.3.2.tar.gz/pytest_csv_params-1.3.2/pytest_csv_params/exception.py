"""
Collection of all plugin specific exceptions. All exceptions are derived from very common base types, such as
:class:`FileNotFoundError`, :class:`IOError` or :class:`ValueError` to ease the exception handling.
"""


class CsvParamsDataFileNotFound(FileNotFoundError):
    """
    This exception is thrown when a CSV file was not found.
    """


class CsvParamsDataFileInaccessible(IOError):
    """
    This exception is thrown when the CSV file is inaccessible.
    """


class CsvParamsDataFileInvalid(ValueError):
    """
    This exception is thrown when a CSV file contains invalid data.

    See the exception message for more details.
    """


class CsvHeaderNameInvalid(ValueError):
    """
    This exception is thrown when a CSV file contains an invalid header name that could not be replaced.
    """
