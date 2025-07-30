# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated

from .._utils import PropertyInfo
from .action_type_config_upsert_base_param import ActionTypeConfigUpsertBaseParam

__all__ = ["UpsertEmailConfigParam"]


class UpsertEmailConfigParam(ActionTypeConfigUpsertBaseParam, total=False):
    body: str
    """Body of the email.

    This can be HTML, and include template variables in the form of
    `{{template_variable}}`. Template variables are taken from the output of the
    transformation.
    """

    from_email: Annotated[str, PropertyInfo(alias="fromEmail")]
    """Email address to send the email from."""

    from_name: Annotated[str, PropertyInfo(alias="fromName")]
    """Name of the sender."""

    subject: str
    """Subject of the email.

    This can include template variables in the form of `{{template_variable}}`.
    Template variables are taken from the output of the transformation.
    """

    to_email: Annotated[str, PropertyInfo(alias="toEmail")]
    """Email address to send the email to."""

    to_name: Annotated[str, PropertyInfo(alias="toName")]
    """Name of the recipient."""
