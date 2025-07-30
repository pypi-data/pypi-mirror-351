# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EmailActionBaseParam"]


class EmailActionBaseParam(TypedDict, total=False):
    template_variables: Required[Annotated[object, PropertyInfo(alias="templateVariables")]]
    """Template variables to be used in the email body and subject.

    Templates are injected into the email body and subject as
    `{{template_variable}}`.
    """
