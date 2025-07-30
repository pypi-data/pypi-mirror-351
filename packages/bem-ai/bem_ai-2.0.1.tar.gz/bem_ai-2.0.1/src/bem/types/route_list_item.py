# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["RouteListItem", "Origin", "OriginEmail", "Regex"]


class OriginEmail(BaseModel):
    patterns: Optional[List[str]] = None
    """
    Regular expression to match against the email address, using the Go (RE2) regex
    syntax.
    """


class Origin(BaseModel):
    email: Optional[OriginEmail] = None


class Regex(BaseModel):
    patterns: Optional[List[str]] = None
    """Regular expression to match against the input, using the Go (RE2) regex syntax."""


class RouteListItem(BaseModel):
    name: str
    """Name of route.

    Should indicate what the input type or intent is to appropriately analyze input.
    """

    action_type_config_id: Optional[str] = FieldInfo(alias="actionTypeConfigID", default=None)
    """ID of action type config to run after routing.

    Currently only Transform Configs are supported.
    """

    description: Optional[str] = None
    """Description of route.

    Can be used to provide additional context on route's purpose.
    """

    origin: Optional[Origin] = None
    """The origin of the route."""

    regex: Optional[Regex] = None
    """Regex to match against the input."""
