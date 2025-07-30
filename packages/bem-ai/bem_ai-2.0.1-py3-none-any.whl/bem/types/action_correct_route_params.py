# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ActionCorrectRouteParams", "RouteAction"]


class ActionCorrectRouteParams(TypedDict, total=False):
    route_actions: Annotated[Iterable[RouteAction], PropertyInfo(alias="routeActions")]
    """
    An array of objects containing all the route actions you want to submit feedback
    for.
    """


class RouteAction(TypedDict, total=False):
    action_id: Annotated[str, PropertyInfo(alias="actionID")]
    """The action ID of the relevant route action."""

    corrected_choice: Annotated[str, PropertyInfo(alias="correctedChoice")]
    """The desired route that should have been chosen."""
