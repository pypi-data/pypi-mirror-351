"""
pyap.address
~~~~~~~~~~~~~~~~

Contains class for constructing Address object which holds information
about address and its components.

:copyright: (c) 2015 by Vladimir Goncharov.
:license: MIT, see LICENSE for more details.
"""

from typing import Any

from pydantic import BaseModel, field_validator


class Address(BaseModel):
    building_id: str | None = None
    city: str | None = None
    country: str | None = None
    country_id: str | None = None
    floor: str | None = None
    full_address: str
    full_street: str | None = None
    match_end: int | str | None = None
    match_start: int | str | None = None
    occupancy: str | None = None
    postal_code: str | None = None
    region1: str | None = None
    route_id: str | None = None
    state: str | None = None
    street: str | None = None
    street_name: str | None = None
    street_number: str | None = None
    street_type: str | None = None

    @field_validator("*", mode="before")
    @classmethod
    def strip_chars(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip(" ,;:")
        if v:
            return v

    def __str__(self) -> str:
        # Address object is represented as textual address
        address = ""
        try:
            address = self.full_address
        except AttributeError:
            pass

        return address
