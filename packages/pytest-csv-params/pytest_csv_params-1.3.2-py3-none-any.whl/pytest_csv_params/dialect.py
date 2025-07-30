"""
Definition of CSV dialects (CSV file formats). At the moment, there is only the default dialect
:class:`~pytest_csv_params.dialect.CsvParamsDefaultDialect`.
"""

import csv


class CsvParamsDefaultDialect(csv.Dialect):  # pylint: disable=too-few-public-methods
    """
    This is the default dialect (or CSV file format) for parametrizing test. It is used when no other dialect is
    defined.

    One can easily adapt it to match your own CSV files. Just use this or :class:`csv.Dialect` as base class.

    See :class:`csv.Dialect` for configuration reference.
    """

    delimiter = ","
    doublequote = True
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    strict = True
    skipinitialspace = True
