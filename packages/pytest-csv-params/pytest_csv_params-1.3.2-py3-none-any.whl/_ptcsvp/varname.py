"""
This module contains code to validate variable/argument/parameter names or to make them valid ones.
"""

import builtins
import keyword
import re
from string import ascii_letters, digits

from pytest_csv_params.exception import CsvHeaderNameInvalid

VALID_CHARS = ascii_letters + digits
"""
Valid characters a variable/parameter/argument name can consist of
"""

VARIABLE_NAME = re.compile(r"^[a-zA-Z_][A-Za-z0-9_]{0,1023}$")
"""
Regular expression that defines a valid variable/parameter/argument name
"""


def is_valid_name(name: str) -> bool:
    """
    Checks if the variable name is valid

    :param name: The name to be checked
    :returns: `True`, when the name is valid
    """
    if (
        keyword.iskeyword(name)
        or (hasattr(keyword, "issoftkeyword") and getattr(keyword, "issoftkeyword")(name))
        or getattr(builtins, name, None) is not None
    ):
        return False
    return VARIABLE_NAME.match(name) is not None


def make_name_valid(name: str, replacement_char: str = "_") -> str:
    """
    Make a name a valid name by replacing invalid chars with the as :attr:`replacement_char` given char

    :param name: The name to make a valid one
    :param replacement_char: The char to replace invalid chars with, default is an underscore `_`
    :returns: A valid name
    :raises CsvHeaderNameInvalid: If the fixed name is still an invalid name
    """

    fixed_name = name

    for index, character in enumerate(name):
        if character in VALID_CHARS:
            continue
        fixed_name = f"{fixed_name[:index]}{replacement_char}{fixed_name[index+1:]}"
    if fixed_name[0] not in ascii_letters:
        fixed_name = f"{replacement_char}{fixed_name[1:]}"
    if not is_valid_name(fixed_name):
        raise CsvHeaderNameInvalid(f"'{fixed_name}' is not a valid variable name")
    return fixed_name
