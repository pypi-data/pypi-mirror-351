# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SubscriptionCreateParams"]


class SubscriptionCreateParams(TypedDict, total=False):
    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]
    """Unique identifier of action this subscription listens to."""

    name: Required[str]
    """Name of subscription."""

    type: Required[Literal["transform", "route", "split_collection", "split_item", "error", "join"]]
    """Type of subscription."""

    disabled: bool
    """Toggles whether subscription is active or not."""

    webhook_url: Annotated[str, PropertyInfo(alias="webhookURL")]
    """URL bem will send webhook requests to."""
