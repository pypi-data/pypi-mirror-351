# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TransformationDeleteResponse"]


class TransformationDeleteResponse(BaseModel):
    delete_count: Optional[int] = FieldInfo(alias="deleteCount", default=None)
    """count of transformations successfully deleted."""
