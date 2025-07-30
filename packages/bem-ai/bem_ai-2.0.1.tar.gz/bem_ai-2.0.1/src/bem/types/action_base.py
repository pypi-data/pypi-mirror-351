# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ActionBase"]


class ActionBase(BaseModel):
    action_id: str = FieldInfo(alias="actionID")

    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")

    reference_id: str = FieldInfo(alias="referenceID")

    status: Literal["pending", "running", "completed", "failed"]
    """The status of the action."""
