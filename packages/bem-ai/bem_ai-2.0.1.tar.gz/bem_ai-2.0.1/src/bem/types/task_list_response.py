# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .task import Task
from .._models import BaseModel

__all__ = ["TaskListResponse"]


class TaskListResponse(BaseModel):
    tasks: Optional[List[Task]] = None

    total_count: Optional[int] = FieldInfo(alias="totalCount", default=None)
    """The total number of results available."""
