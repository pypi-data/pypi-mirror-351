"""
pyap.utils
~~~~~~~~~~~~~~~~

This module provides some utility functions.

:copyright: (c) 2015 by Vladimir Goncharov.
:license: MIT, see LICENSE for more details.
"""

import re
from re import Match, RegexFlag

DEFAULT_FLAGS = re.VERBOSE | re.UNICODE


def match(regex: str, string: str, flags: RegexFlag = DEFAULT_FLAGS) -> Match | None:
    """Utility function for re.match"""
    return re.match(regex, string, flags=flags)


def findall(
    regex: str, string: str, flags: RegexFlag = DEFAULT_FLAGS
) -> list[Match | None]:
    """Utility function for re.findall"""
    return re.findall(regex, string, flags=flags)


def finditer(regex: str, string: str, flags: RegexFlag = DEFAULT_FLAGS) -> list[Match]:
    """Utility function for re.finditer"""
    return list(re.finditer(regex, string, flags=flags))
