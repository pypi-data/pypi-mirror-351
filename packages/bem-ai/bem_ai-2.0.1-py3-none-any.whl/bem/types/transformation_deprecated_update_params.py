# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformationDeprecatedUpdateParams", "Transformation"]


class TransformationDeprecatedUpdateParams(TypedDict, total=False):
    transformations: Iterable[Transformation]
    """An array of objects containing all the transformations you want to patch."""


class Transformation(TypedDict, total=False):
    corrected_json: Annotated[Optional[object], PropertyInfo(alias="correctedJSON")]
    """The object with properties of the transformation that you want updated."""

    order_matching: Annotated[Optional[bool], PropertyInfo(alias="orderMatching")]
    """True if order in the array matters. Default is false."""

    transformation_id: Annotated[str, PropertyInfo(alias="transformationID")]
    """The unique ID you use internally to refer to a transform."""
