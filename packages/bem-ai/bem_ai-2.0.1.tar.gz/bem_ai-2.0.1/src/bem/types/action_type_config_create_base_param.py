# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .action_type import ActionType

__all__ = ["ActionTypeConfigCreateBaseParam"]


class ActionTypeConfigCreateBaseParam(TypedDict, total=False):
    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""
