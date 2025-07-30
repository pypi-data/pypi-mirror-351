# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RouteListItemParam", "Origin", "OriginEmail", "Regex"]


class OriginEmail(TypedDict, total=False):
    patterns: List[str]
    """
    Regular expression to match against the email address, using the Go (RE2) regex
    syntax.
    """


class Origin(TypedDict, total=False):
    email: OriginEmail


class Regex(TypedDict, total=False):
    patterns: List[str]
    """Regular expression to match against the input, using the Go (RE2) regex syntax."""


class RouteListItemParam(TypedDict, total=False):
    name: Required[str]
    """Name of route.

    Should indicate what the input type or intent is to appropriately analyze input.
    """

    action_type_config_id: Annotated[str, PropertyInfo(alias="actionTypeConfigID")]
    """ID of action type config to run after routing.

    Currently only Transform Configs are supported.
    """

    description: str
    """Description of route.

    Can be used to provide additional context on route's purpose.
    """

    origin: Origin
    """The origin of the route."""

    regex: Regex
    """Regex to match against the input."""
