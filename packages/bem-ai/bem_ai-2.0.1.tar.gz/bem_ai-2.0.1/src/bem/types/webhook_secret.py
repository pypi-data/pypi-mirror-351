# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["WebhookSecret"]


class WebhookSecret(BaseModel):
    secret: str
    """Webhook secret for your account."""
