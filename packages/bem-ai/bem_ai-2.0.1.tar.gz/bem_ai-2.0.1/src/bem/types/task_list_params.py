# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .task_status import TaskStatus

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is a task ID that defines your place in the list. For example, if
    you make a list request and receive 50 objects, starting with
    `tsk_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `endingBefore=tsk_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the previous page of the
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
    `tsk_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `startingAfter=tsk_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the next page of the
    list.
    """

    status: TaskStatus
    """Array with the task statuses, formatted as a CSV array."""

    task_ids: Annotated[List[str], PropertyInfo(alias="taskIDs")]
    """Array with the task IDs, formatted as a CSV array."""
