# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .input_type import InputType

__all__ = ["JoinActionBase", "Input"]


class Input(BaseModel):
    input_content: str = FieldInfo(alias="inputContent")
    """The file content you want to transform as a base64 encoded string.

    If the `inputType` is `email`, this is equivalent to the raw format returned by
    the Gmail API.
    """

    input_type: InputType = FieldInfo(alias="inputType")
    """The input type of the content you're sending for transformation."""

    item_reference_id: Optional[str] = FieldInfo(alias="itemReferenceID", default=None)
    """The unique ID you use internally to refer to this data point."""


class JoinActionBase(BaseModel):
    inputs: List[Input]

    join_type: Literal["standard"] = FieldInfo(alias="joinType")
