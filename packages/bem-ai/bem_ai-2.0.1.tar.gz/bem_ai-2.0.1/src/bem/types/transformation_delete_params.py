# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformationDeleteParams"]


class TransformationDeleteParams(TypedDict, total=False):
    pipeline_id: Annotated[str, PropertyInfo(alias="pipelineID")]
    """The unique ID for a given pipeline.

    Will filter to just the transformations processed by the given pipeline. If left
    out, will query over ALL transformations for your account.
    """

    reference_ids: Annotated[List[str], PropertyInfo(alias="referenceIDs")]
    """Array with the reference IDs of the transformed data points.

    Formatted as a CSV array.
    """

    transformation_ids: Annotated[List[str], PropertyInfo(alias="transformationIDs")]
    """Array with the transform IDs of the transformed data points.

    Formatted as a CSV array.
    """
