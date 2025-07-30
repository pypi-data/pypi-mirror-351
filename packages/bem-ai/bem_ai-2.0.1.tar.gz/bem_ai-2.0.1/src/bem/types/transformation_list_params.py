# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformationListParams"]


class TransformationListParams(TypedDict, total=False):
    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is a transform ID that defines your place in the list. For
    example, if you make a list request and receive 50 objects, starting with
    `tr_2bxoJPNdSD4LgRT4YVC4gt72hlI`, your subsequent call can include
    `endingBefore=tr_2bxoJPNdSD4LgRT4YVC4gt72hlI` to fetch the previous page of the
    list.
    """

    item_offset: Annotated[int, PropertyInfo(alias="itemOffset")]
    """Filters based on the index of the page of the document you had transformed.

    For CSV transformations, this offset represents starting row of the CSV for
    which you want to fetch transformations for. For PDF transformations, this
    offset represents the starting page of the PDF. This applies for a specific
    reference ID of a transformation. Note that this only applies if you specify one
    reference ID in `referenceIDs` and if you have
    `independentDocumentProcessingEnabled` set to `true` in your pipeline
    configuration. Note that this is zero-indexed.
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

    published: bool
    """
    Boolean that toggles filtering whether or not transformations were successfully
    published via webhook.
    """

    published_after: Annotated[Union[str, datetime], PropertyInfo(alias="publishedAfter", format="iso8601")]
    """
    Filters to transformations successfully published via webhook after the
    specified date. Must be in RFC 3339 format.
    """

    published_before: Annotated[Union[str, datetime], PropertyInfo(alias="publishedBefore", format="iso8601")]
    """
    Filters to transformations successfully published via webhook before the
    specified date. Must be in RFC 3339 format.
    """

    reference_ids: Annotated[List[str], PropertyInfo(alias="referenceIDs")]
    """Array with the reference IDs of the transformed data points.

    Formatted as a CSV array.
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

    transformation_ids: Annotated[List[str], PropertyInfo(alias="transformationIDs")]
    """Array with the transform IDs of the transformed data points.

    Formatted as a CSV array.
    """
