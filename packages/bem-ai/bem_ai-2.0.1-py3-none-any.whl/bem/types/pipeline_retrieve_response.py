# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .pipeline import Pipeline

__all__ = ["PipelineRetrieveResponse"]


class PipelineRetrieveResponse(BaseModel):
    pipeline: Optional[Pipeline] = None
