# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .event import Event
from .._models import BaseModel

__all__ = ["EventListResponse"]


class EventListResponse(BaseModel):
    events: Optional[List[Event]] = None

    total_count: Optional[int] = FieldInfo(alias="totalCount", default=None)
    """The total number of results available."""
