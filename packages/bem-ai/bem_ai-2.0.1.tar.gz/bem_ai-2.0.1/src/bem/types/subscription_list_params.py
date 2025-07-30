# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SubscriptionListParams"]


class SubscriptionListParams(TypedDict, total=False):
    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is a task ID that defines your place in the list. For example, if
    you make a list request and receive 50 objects, starting with
    `sub_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `endingBefore=sub_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the previous page of the
    list.
    """

    limit: int
    """
    This specifies a limit on the number of objects to return, ranging between 1
    and 100.
    """

    sort_order: Annotated[Literal["asc", "desc"], PropertyInfo(alias="sortOrder")]
    """Specifies sorting behavior.

    The two options are `asc` and `desc` to sort ascending and descending
    respectively, with default sort being ascending. Paging works in both
    directions.
    """

    starting_after: Annotated[str, PropertyInfo(alias="startingAfter")]
    """A cursor to use in pagination.

    `startingAfter` is a task ID that defines your place in the list. For example,
    if you make a list request and receive 50 objects, ending with
    `sub_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `startingAfter=sub_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the next page of the
    list.
    """
