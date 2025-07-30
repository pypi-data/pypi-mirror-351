"""
This module contains the main plugin class. By the time of writing, it is quite unspectacular.
"""

from _pytest.config import Config

BASE_DIR_KEY = "__pytest_csv_params__config__base_dir"
"""
The class attribute key for :class:`Plugin` to store the base dir command line argument value.
"""


class Plugin:  # pylint: disable=too-few-public-methods
    """
    The main plugin class

    Currently, this class is nothing more than the keeper of the value of the command line argument (as defined by
    :meth:`_ptcsvp.cmdline.pytest_addoption`.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the class, and simply store the value of the command line argument, as class attribute.

        :param config: Pytest configuration
        """
        setattr(Plugin, BASE_DIR_KEY, config.option.csv_params_base_dir)
