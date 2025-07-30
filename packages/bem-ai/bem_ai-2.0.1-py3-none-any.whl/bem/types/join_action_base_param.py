# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo
from .._models import set_pydantic_config
from .input_type import InputType

__all__ = ["JoinActionBaseParam", "Input"]


class Input(TypedDict, total=False):
    input_content: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(alias="inputContent", format="base64")]]
    """The file content you want to transform as a base64 encoded string.

    If the `inputType` is `email`, this is equivalent to the raw format returned by
    the Gmail API.
    """

    input_type: Required[Annotated[InputType, PropertyInfo(alias="inputType")]]
    """The input type of the content you're sending for transformation."""

    item_reference_id: Annotated[str, PropertyInfo(alias="itemReferenceID")]
    """The unique ID you use internally to refer to this data point."""


set_pydantic_config(Input, {"arbitrary_types_allowed": True})


class JoinActionBaseParam(TypedDict, total=False):
    inputs: Required[Iterable[Input]]

    join_type: Required[Annotated[Literal["standard"], PropertyInfo(alias="joinType")]]
