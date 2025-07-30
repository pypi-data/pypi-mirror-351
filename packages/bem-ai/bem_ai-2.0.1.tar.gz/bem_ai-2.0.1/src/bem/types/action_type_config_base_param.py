# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ActionTypeConfigBaseParam"]


class ActionTypeConfigBaseParam(TypedDict, total=False):
    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]
    """Unique identifier of action type config."""

    name: Required[str]
    """Name of action type config."""
