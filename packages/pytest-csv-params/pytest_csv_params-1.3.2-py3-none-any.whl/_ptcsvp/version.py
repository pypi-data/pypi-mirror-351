"""
This module contains two methods to check if the python version is recent enough (:meth:`check_python_version`) and if
the pytest version is recent enough (:meth:`check_pytest_version`).

During the setup phase of the plugin (see :mod:`pytest_csv_params.plugin`) these methods are called.
"""

import sys
from typing import Tuple

from attr.exceptions import PythonTooOldError
from packaging.version import parse


def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> None:
    """
    Check if the current version is at least 3.8

    :param min_version: The minimum version required, as tuple, default is 3.8
    :raises PythonTooOldError: When the python version is too old/unsupported
    """

    if sys.version_info < min_version:
        raise PythonTooOldError(f"At least Python {'.'.join(map(str, min_version))} required")


def check_pytest_version(min_version: Tuple[int, int] = (7, 4)) -> None:
    """
    Check if the current version is at least 7.4

    :param min_version: The minimum version required, as tuple, default is 7.4
    :raises RuntimeError: When the pytest version is too old/unsupported
    """

    from pytest import __version__ as pytest_version  # pylint: disable=import-outside-toplevel

    pytest_min_version = ".".join(map(str, min_version))
    parsed_min_version = parse(pytest_min_version)
    parsed_actual_version = parse(pytest_version)
    if parsed_actual_version < parsed_min_version:
        raise RuntimeError(f"At least Pytest {pytest_min_version} required")
