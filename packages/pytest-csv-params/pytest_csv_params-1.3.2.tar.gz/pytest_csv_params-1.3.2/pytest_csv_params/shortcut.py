"""
Shortcut decorators
"""

from pytest_csv_params.decorator import csv_params as default_csv_params


def csv_params_reusing_id_col(**kwargs):
    """
    Shortcut decorator that allows to re-use ID columns as data columns
    """
    kwargs.setdefault("reuse_id_col", True)
    return default_csv_params(**kwargs)
