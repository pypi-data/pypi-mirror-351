# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SubscriptionUpdateParams"]


class SubscriptionUpdateParams(TypedDict, total=False):
    action_type_config_id: Annotated[str, PropertyInfo(alias="actionTypeConfigID")]
    """Unique identifier of action this subscription listens to."""

    disabled: bool
    """Toggles whether subscription is active or not."""

    name: str
    """Name of subscription."""

    type: Literal["transform", "route", "split_collection", "split_item", "error", "join"]
    """Type of subscription."""

    webhook_url: Annotated[str, PropertyInfo(alias="webhookURL")]
    """URL bem will send webhook requests to."""
