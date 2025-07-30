# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SplitConfigSemanticPageItemClassParam"]


class SplitConfigSemanticPageItemClassParam(TypedDict, total=False):
    name: Required[str]

    description: str

    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """The unique ID of the action type configuration you want to use for this action."""
