"""
The pytest plugin needs a setup (:meth:`pytest_configure`) and a teardown (:meth:`pytest_unconfigure`) method
registered. This module contains the required methods for that.
"""

from _pytest.config import Config

from _ptcsvp.plugin import Plugin


def pytest_configure(config: Config, plugin_name: str = "csv_params") -> None:
    """
    Register our Plugin

    :param config: Pytets configuration class
    :param plugin_name: The name of the pytest plugin, with default value
    """
    config.pluginmanager.register(Plugin(config), name=f"{plugin_name}_plugin")


def pytest_unconfigure(config: Config, plugin_name: str = "csv_params") -> None:
    """
    Remove our Plugin

    :param config: Pytest configuration class
    :param plugin_name: The name of the pytest plgin, with default value
    """
    config.pluginmanager.unregister(name=f"{plugin_name}_plugin")
