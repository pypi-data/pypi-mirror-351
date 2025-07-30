# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformationListErrorsParams"]


class TransformationListErrorsParams(TypedDict, total=False):
    reference_ids: Required[Annotated[List[str], PropertyInfo(alias="referenceIDs")]]
    """Array with the reference IDs of the transformed data points.

    Formatted as a CSV array.
    """

    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is a transform ID that defines your place in the list. For
    example, if you make a list request and receive 50 objects, starting with
    `tr_2bxoJPNdSD4LgRT4YVC4gt72hlI`, your subsequent call can include
    `endingBefore=tr_2bxoJPNdSD4LgRT4YVC4gt72hlI` to fetch the previous page of the
    list.
    """

    limit: int
    """
    This specifies a limit on the number of objects to return, ranging between 1
    and 100.
    """

    pipeline_id: Annotated[str, PropertyInfo(alias="pipelineID")]
    """The unique ID for a given pipeline.

    Will filter to just the transformations processed by the given pipeline. If left
    out, will query over ALL transformations for your account.
    """

    sort_order: Annotated[Literal["asc", "desc"], PropertyInfo(alias="sortOrder")]
    """Specifies sorting behavior.

    The two options are `asc` and `desc` to sort ascending and descending
    respectively, with default sort being ascending. Paging works in both
    directions.
    """

    starting_after: Annotated[str, PropertyInfo(alias="startingAfter")]
    """A cursor to use in pagination.

    `startingAfter` is a transform ID that defines your place in the list. For
    example, if you make a list request and receive 50 objects, ending with
    `tr_2bxoJPNdSD4LgRT4YVC4gt72hlI`, your subsequent call can include
    `startingAfter=tr_2bxoJPNdSD4LgRT4YVC4gt72hlI` to fetch the next page of the
    list.
    """
