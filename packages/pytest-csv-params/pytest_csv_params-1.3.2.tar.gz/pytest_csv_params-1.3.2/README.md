![pytest-csv-params](https://docs.codebau.dev/pytest-plugins/pytest-csv-params/_images/pytest-csv-params.png)

# pytest-csv-params

A pytest plugin to parametrize data-driven tests by CSV files.

[![Build Status](https://build.codebau.dev/buildStatus/icon?job=pytest-csv-params&style=flat)](https://git.codebau.dev/pytest-plugins/pytest-csv-params)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/pytest-csv-params?label=PyPI%20downloads&style=flat&logo=pypi)](https://pypi.org/project/pytest-csv-params/)
[![PyPI - Version](https://img.shields.io/pypi/v/pytest-csv-params?label=PyPI%20version&style=flat&logo=pypi)](https://pypi.org/project/pytest-csv-params/)
[![PyPI - Status](https://img.shields.io/pypi/status/pytest-csv-params?label=PyPI%20status&style=flat&logo=pypi)](https://pypi.org/project/pytest-csv-params/)
[![PyPI - Format](https://img.shields.io/pypi/format/pytest-csv-params?label=PyPI%20format&style=flat&logo=pypi)](https://pypi.org/project/pytest-csv-params/)

## Requirements
 
- Python 3.9, 3.10, 3.11, 3.12, 3.13
- pytest >= 8.3

There's no operating system dependent code in this plugin, so it should run anywhere where pytest runs.

## Installation

Simply install it with pip...

```bash
pip install pytest-csv-params
```

... or poetry ...

```bash
poetry add --group dev pytest-csv-params
```

## Documentation / User Guide

**Detailed documentation can be found under
[docs.codebau.dev/pytest-plugins/pytest-csv-params/](https://docs.codebau.dev/pytest-plugins/pytest-csv-params/)**

## Usage: Command Line Argument

| Argument                | Required      | Description                                                          | Example                                      |
|-------------------------|---------------|----------------------------------------------------------------------|----------------------------------------------|
| `--csv-params-base-dir` | no (optional) | Define a base dir for all relative-path CSV data files (since 0.1.0) | `pytest --csv-params-base-dir /var/testdata` |

## Usage: Decorator

Simply decorate your test method with `@csv_params` (`pytest_csv_params.decorator.csv_params`) and the following parameters:

| Parameter        | Type                     | Description                                                                                                                            | Example                                                                                        |
|------------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `data_file`      | `str`                    | The CSV file to use, relative or absolute path                                                                                         | `"/var/testdata/test1.csv"`                                                                    |
| `base_dir`       | `str` (optional)         | Directory to look up relative CSV files (see `data_file`); overrides the command line argument                                         | `join(dirname(__file__), "assets")`                                                            |
| `id_col`         | `str` (optional)         | Column name of the CSV that contains test case IDs                                                                                     | `"ID#"`                                                                                        |
| `dialect`        | `csv.Dialect` (optional) | CSV Dialect definition (see [Python CSV Documentation](https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters)) | `csv.excel_tab`                                                                                |
| `data_casts`     | `dict` (optional)        | Cast Methods for the CSV Data (see "Data Casting" below)                                                                               | `{ "a": int, "b": float }`                                                                     |
| `header_renames` | `dict` (optional)        | Replace headers from the CSV file, so that they can be used as parameters for the test function (since 0.3.0)                          | `{ "Annual Amount of Bananas": "banana_count", "Cherry export price": "cherry_export_price" }` | 
| `reuse_id_col`   | `bool` (optional)        | Allows to re-use the ID column as test data column (since 1.3.0), defaults to `False` for backwards compatibility                      | `True`                                                                                         | 

## CSV Format

The default CSV format is:

- `\r\n` as line ending
- All non-numeric fields are surrounded by `"`
- If you need a `"` in the value, use `""` (double quote)
- Fields are separated by comma (`,`)

## Usage Example

This example uses the CSV example from above.

```python
from pytest_csv_params.decorator import csv_params

@csv_params(
    data_file="/data/test-lib/cases/addition.csv",
    id_col="ID#",
    data_casts={
        "part_a": int,
        "part_b": int,
        "expected_result": int,
    },
)
def test_addition(part_a, part_b, expected_result):
    assert part_a + part_b == expected_result
```

Shorthand example (no ID col, only string values):

```python
from pytest_csv_params.decorator import csv_params

@csv_params("/data/test-lib/cases/texts.csv")
def test_texts(text_a, text_b, text_c):
    assert f"{text_a}:{text_b}" == text_c
```

### More complex example

This example features nearly all things the plugin has to offer. You find this example also in the test cases, see `tests/test_complex_example.py`.

The CSV file (`tests/assets/example.csv`):

```text
"Test ID","Bananas shipped","Single Banana Weight","Apples shipped","Single Apple Weight","Container Size"
"Order-7","1503","0.5","2545","0.25","1500"
"Order-15","101","0.55","1474","0.33","550"
```

The Test (`tests/test_complex_example.py`):

```python
from math import ceil
from os.path import join, dirname

from pytest_csv_params.decorator import csv_params


@csv_params(
    data_file="example.csv",
    base_dir=join(dirname(__file__), "assets"),
    id_col="Test ID",
    header_renames={
        "Bananas shipped": "bananas_shipped",
        "Single Banana Weight": "banana_weight",
        "Apples shipped": "apples_shipped",
        "Single Apple Weight": "apple_weight",
        "Container Size": "container_size",
    },
    data_casts={
        "bananas_shipped": int,
        "banana_weight": float,
        "apples_shipped": int,
        "apple_weight": float,
        "container_size": int,
    },
)
def test_container_size_is_big_enough(
    bananas_shipped: int, banana_weight: float, apples_shipped: int, apple_weight: float, container_size: int
) -> None:
    """
    This is just an example test case for the documentation.
    """

    gross_weight = (banana_weight * bananas_shipped) + (apple_weight * apples_shipped)
    assert ceil(gross_weight) <= container_size
```

If you decide not to rename the columns, the test would look like this:

```python
@csv_params(
    data_file="example.csv",
    base_dir=join(dirname(__file__), "assets"),
    id_col="Test ID",
    data_casts={
        "Bananas_Shipped": int,
        "Single_Banana_Weight": float,
        "Apples_Shipped": int,
        "Single_Apple_Weight": float,
        "Container_Size": int,
    },
)
def test_container_size_is_big_enough(
    Bananas_Shipped: int, Single_Banana_Weight: float, Apples_Shipped: int, Single_Apple_Weight: float, Container_Size: int
) -> None:
    ...
```

## Changelog

- A detailed changelog is here:
  [docs.codebau.dev/pytest-plugins/pytest-csv-params/pages/changelog.html](https://docs.codebau.dev/pytest-plugins/pytest-csv-params/pages/changelog.html)

## Bugs etc.

Please send your issues to `csv-params_issues` (at) `jued.de`. Please include the following:

- Plugin Version used
- Pytest version
- Python version with operating system

It would be great if you could include example code that clarifies your issue.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Pull Requests

Pull requests are always welcome. Since this Gitea instance is not open to public, just send an e-mail to discuss options.

Any changes that are made are to be backed by tests. Please give me a sign if you're going to break the existing API and let us discuss ways to handle that.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Where are the sources?

The source code is available under [git.codebau.dev/pytest-plugins/pytest-csv-params](https://git.codebau.dev/pytest-plugins/pytest-csv-params).
