# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ActionTypeConfigBase"]


class ActionTypeConfigBase(BaseModel):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """Unique identifier of action type config."""

    name: str
    """Name of action type config."""
