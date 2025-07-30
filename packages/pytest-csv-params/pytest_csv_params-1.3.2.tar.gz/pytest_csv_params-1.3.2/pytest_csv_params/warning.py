"""
Definitions of all Warnings used in the Plugin
"""

from _pytest.warning_types import PytestWarning


class CsvParamsWarning(PytestWarning):
    """
    Base class for all PytestCsvParams Plugin Warnings

    Use this class if you want to filter out all the warnings of this Plugin
    """


class CsvParamsOnlyOneColumnIsUsedAsIdAndDataWarning(CsvParamsWarning):
    """
    Raised when only a single column is used for ID and test data, which is
    most likely a configuration error, but might be valid in some scenarios.
    """
