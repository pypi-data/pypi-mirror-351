"""
This pytest plugin requires command line arguments that are parsed from the pytest framework. This module contains code
to instruct pytest to deliver the required values.
"""

from _pytest.config.argparsing import Parser

HELP_TEXT = "set base dir for getting CSV data files from"
"""
This is the help text for the command line arguments that is added by :meth:`pytest_addoption`.
"""


def pytest_addoption(parser: Parser, plugin_name: str = "csv-params") -> None:
    """
    Entrypoint for pytest to extend the own :class:`Parser` with the things we need extra.

    :param parser: The pytest command line argument parser
    :param plugin_name: The name of our plugin, with default value
    """

    group = parser.getgroup(plugin_name)
    group.addoption(
        f"--{plugin_name}-base-dir",
        action="store",
        type=str,
        default=None,
        required=False,
        help=HELP_TEXT,
    )
