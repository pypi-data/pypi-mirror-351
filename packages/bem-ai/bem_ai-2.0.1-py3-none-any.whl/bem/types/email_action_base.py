# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EmailActionBase"]


class EmailActionBase(BaseModel):
    template_variables: object = FieldInfo(alias="templateVariables")
    """Template variables to be used in the email body and subject.

    Templates are injected into the email body and subject as
    `{{template_variable}}`.
    """
