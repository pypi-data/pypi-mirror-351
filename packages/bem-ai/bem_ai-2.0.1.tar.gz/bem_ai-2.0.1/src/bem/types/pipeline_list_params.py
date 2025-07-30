# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PipelineListParams"]


class PipelineListParams(TypedDict, total=False):
    ending_before: Annotated[str, PropertyInfo(alias="endingBefore")]
    """A cursor to use in pagination.

    `endingBefore` is a pipeline ID that defines your place in the list. For
    example, if you make a list request and receive 50 objects, starting with
    `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `endingBefore=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the previous page of the
    list.
    """

    limit: int

    starting_after: Annotated[str, PropertyInfo(alias="startingAfter")]
    """A cursor to use in pagination.

    `startingAfter` is a pipeline ID that defines your place in the list. For
    example, if you make a list request and receive 50 objects, ending with
    `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can include
    `startingAfter=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the next page of the
    list.
    """
