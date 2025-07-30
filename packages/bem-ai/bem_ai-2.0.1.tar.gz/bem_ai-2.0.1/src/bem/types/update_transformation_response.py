# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["UpdateTransformationResponse", "Result"]


class Result(BaseModel):
    error: Optional[str] = None
    """error message"""

    success: Optional[bool] = None

    transformation_id: Optional[str] = FieldInfo(alias="transformationID", default=None)
    """The unique ID you use internally to refer to a transform."""


class UpdateTransformationResponse(BaseModel):
    results: Optional[List[Result]] = None
    """An array of objects containing all the transformations you want to patch."""

    success_count: Optional[int] = FieldInfo(alias="successCount", default=None)

    total_count: Optional[int] = FieldInfo(alias="totalCount", default=None)
