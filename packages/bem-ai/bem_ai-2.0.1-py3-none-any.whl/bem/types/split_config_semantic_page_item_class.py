# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SplitConfigSemanticPageItemClass"]


class SplitConfigSemanticPageItemClass(BaseModel):
    name: str

    description: Optional[str] = None

    next_action_type_config_id: Optional[str] = FieldInfo(alias="nextActionTypeConfigID", default=None)
    """The unique ID of the action type configuration you want to use for this action."""
