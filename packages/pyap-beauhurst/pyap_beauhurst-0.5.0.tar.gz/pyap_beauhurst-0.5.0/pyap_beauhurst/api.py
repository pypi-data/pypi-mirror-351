"""
pyap.api
~~~~~~~~~~~~~~~~

This module contains address parser API functions.

:copyright: (c) 2015 by Vladimir Goncharov.
:license: MIT, see LICENSE for more details.
"""

from typing import Any

from pyap_beauhurst.address import Address

from . import parser


def parse(some_text: str, **kwargs: Any) -> list[Address | None]:
    """Creates request to AddressParser
    and returns list of Address objects
    """
    ap = parser.AddressParser(**kwargs)
    return ap.parse(some_text)
