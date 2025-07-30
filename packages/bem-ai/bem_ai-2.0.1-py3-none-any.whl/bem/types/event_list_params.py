# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EventListParams"]


class EventListParams(TypedDict, total=False):
    action_type_config_ids: Annotated[List[str], PropertyInfo(alias="actionTypeConfigIDs")]

    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is an event ID that defines your place in the list.
    """

    event_ids: Annotated[List[str], PropertyInfo(alias="eventIDs")]

    event_types: Annotated[
        List[Literal["transform", "route", "split_collection", "split_item", "error", "join"]],
        PropertyInfo(alias="eventTypes"),
    ]

    limit: int

    reference_ids: Annotated[List[str], PropertyInfo(alias="referenceIDs")]

    sort_order: Annotated[Literal["asc", "desc"], PropertyInfo(alias="sortOrder")]
    """Specifies sorting behavior.

    The two options are `asc` and `desc` to sort ascending and descending
    respectively, with default sort being ascending. Paging works in both
    directions.
    """

    starting_after: Annotated[str, PropertyInfo(alias="startingAfter")]
    """A cursor to use in pagination.

    `startingAfter` is an event ID that defines your place in the list.
    """
