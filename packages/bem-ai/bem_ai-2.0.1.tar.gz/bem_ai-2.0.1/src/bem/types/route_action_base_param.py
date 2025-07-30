# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .input_type import InputType

__all__ = ["RouteActionBaseParam"]


class RouteActionBaseParam(TypedDict, total=False):
    input_content: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(alias="inputContent", format="base64")]]
    """The file content you want to route as a base64 encoded string.

    If the `inputType` is `email`, this is equivalent to the raw format returned by
    the Gmail API.
    """

    input_type: Required[Annotated[InputType, PropertyInfo(alias="inputType")]]
    """The input type of the content you're sending for transformation."""


set_pydantic_config(RouteActionBaseParam, {"arbitrary_types_allowed": True})
