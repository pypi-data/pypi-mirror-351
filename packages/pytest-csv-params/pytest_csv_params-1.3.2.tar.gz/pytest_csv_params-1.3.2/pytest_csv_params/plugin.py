"""
Pytest Plugin Entrypoint:
This module contains all the code to initialize the pytest plugin. This is the entrypoint configured in the
`pyproject.toml` as `pytest11`.
"""

from _ptcsvp.cmdline import pytest_addoption as _pytest_addoption
from _ptcsvp.configure import pytest_configure as _pytest_configure
from _ptcsvp.configure import pytest_unconfigure as _pytest_unconfigure
from _ptcsvp.version import check_pytest_version, check_python_version

# Fist at all, check if the python & pytest version matches
check_python_version()
check_pytest_version()

# Basic config
pytest_configure = _pytest_configure
"""
Hook our :meth:`_ptcsvp.configure.pytest_configure` method to setup the plugin setup
"""

pytest_unconfigure = _pytest_unconfigure
"""
Hook our :meth:`_ptcsvp.configure.pytest_unconfigure` method to setup the plugin teardown
"""

# Command Line Arguments
pytest_addoption = _pytest_addoption
"""
Hook our :meth:`_ptcsvp.cmdline.pytest_addoption` method to setup our command line arguments
"""
