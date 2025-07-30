"""
This module contains type definitions to ease the usage of the API and its documentation.

Some types are somewhat complex, and it is easier to use a single word/reference instead of a complex typing construct.
"""

import csv
from typing import Any, Callable, Dict, Optional, Type

DataCast = Callable[[str], Any]
"""
A :class:`DataCast` describes how a data casting callable must be implemented. It requires one parameter of the type
:class:`str` and can return anything that is required.
"""

DataCastDict = Dict[str, DataCast]
"""
A :class:`DataCastDict` describes how a dictionary of data casting callables must look like. The key is a :class:`str`
describing the column name, the value is a :class:`DataCast`.
"""

DataCasts = Optional[DataCastDict]
"""
The :class:`DataCasts` type describes the type of the `data_casts` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator. An optional :class:`DataCastDict`.
"""

BaseDir = Optional[str]
"""
The :class:`BaseDir` describes the type of the `base_dir` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator to search for non-absolute CSV files. It is simply an optional
:class:`str`.
"""

IdColName = Optional[str]
"""
The :class:`IdColName` describes the type of the `id_col` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator to name the ID column from a CSV file. It is simply an
optional :class:`str`.
"""

DataFile = str
"""
The :class:`DataFile` describes the type if the `data_file` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator to define the CSV file to use. It is an obligatory
:class:`str`.
"""

CsvDialect = Type[csv.Dialect]
"""
The :class:`CsvDialect` describes the type of the `dialect` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator. It is required, but it has an default value in
:class:`pytest_csv_params.dialect.CsvParamsDefaultDialect`.
"""

HeaderRenamesDict = Dict[str, str]
"""
The :class:`HeaderRenamesDict` describes how a dictionary of header renames must look. Keys and values must both be of
type :class:`str`.
"""

HeaderRenames = Optional[HeaderRenamesDict]
"""
The :class:`HeaderRenames` describes the type of the `header_renames` parameter of the
:meth:`~pytest_csv_params.decorator.csv_params` decorator. It is just an optional :class:`HeaderRenamesDict`.
"""
