# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Subscription"]


class Subscription(BaseModel):
    name: str
    """Name of subscription."""

    subscription_id: str = FieldInfo(alias="subscriptionID")
    """The unique identifier of the subscription."""

    type: Literal["transform", "route", "split_collection", "split_item", "error", "join"]
    """Type of subscription."""

    action_type_config_id: Optional[str] = FieldInfo(alias="actionTypeConfigID", default=None)
    """Unique identifier of action subscription listens to.

    Only associated with pipeline IDs at the moment.
    """

    disabled: Optional[bool] = None
    """Toggles whether subscription is active or not."""

    webhook_url: Optional[str] = FieldInfo(alias="webhookURL", default=None)
    """URL bem will send webhook requests to."""
