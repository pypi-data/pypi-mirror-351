"""
This module defines/publishes the main decorator.
"""

from _ptcsvp.parametrize import add_parametrization

csv_params = add_parametrization
"""
Decorator ``@csv_params``

For supported arguments, see :py:meth:`~_ptcsvp.parametrize.add_parametrization`.
"""
