# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .input_type import InputType

__all__ = ["RouteActionBase"]


class RouteActionBase(BaseModel):
    input_content: str = FieldInfo(alias="inputContent")
    """The file content you want to route as a base64 encoded string.

    If the `inputType` is `email`, this is equivalent to the raw format returned by
    the Gmail API.
    """

    input_type: InputType = FieldInfo(alias="inputType")
    """The input type of the content you're sending for transformation."""
