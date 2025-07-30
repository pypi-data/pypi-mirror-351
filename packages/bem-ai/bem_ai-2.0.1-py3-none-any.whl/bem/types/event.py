# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .event_base import EventBase

__all__ = [
    "Event",
    "TransformEvent",
    "RouteEvent",
    "SplitCollectionEvent",
    "SplitCollectionEventPrintPageOutput",
    "SplitCollectionEventPrintPageOutputItem",
    "SplitCollectionEventSemanticPageOutput",
    "SplitCollectionEventSemanticPageOutputItem",
    "SplitItemEvent",
    "SplitItemEventPrintPageOutput",
    "SplitItemEventSemanticPageOutput",
    "ErrorEvent",
    "JoinEvent",
    "JoinEventItem",
]


class TransformEvent(EventBase):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """
    Unique identifier of action type configuration that this event is associated
    with.
    """

    item_count: int = FieldInfo(alias="itemCount")
    """The number of items that were transformed.

    Used for batch transformations to indicate how many items were transformed.
    """

    item_offset: int = FieldInfo(alias="itemOffset")
    """The offset of the first item that was transformed.

    Used for batch transformations to indicate which item in the batch this event
    corresponds to.
    """

    transformed_content: object = FieldInfo(alias="transformedContent")
    """The transformed content of the input.

    The structure of this object is defined by the action type configuration.
    """

    event_type: Optional[Literal["transform"]] = FieldInfo(alias="eventType", default=None)

    invalid_properties: Optional[List[str]] = FieldInfo(alias="invalidProperties", default=None)
    """List of properties that were invalid in the input."""


class RouteEvent(EventBase):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """
    Unique identifier of action type configuration that this event is associated
    with.
    """

    choice: str
    """The choice made by the router action."""

    event_type: Optional[Literal["route"]] = FieldInfo(alias="eventType", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)
    """The presigned S3 URL of the file that was routed."""


class SplitCollectionEventPrintPageOutputItem(BaseModel):
    item_offset: Optional[int] = FieldInfo(alias="itemOffset", default=None)

    item_reference_id: Optional[str] = FieldInfo(alias="itemReferenceID", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)
    """The presigned S3 URL of the file that was split."""


class SplitCollectionEventPrintPageOutput(BaseModel):
    item_count: Optional[int] = FieldInfo(alias="itemCount", default=None)

    items: Optional[List[SplitCollectionEventPrintPageOutputItem]] = None


class SplitCollectionEventSemanticPageOutputItem(BaseModel):
    item_class: Optional[str] = FieldInfo(alias="itemClass", default=None)

    item_class_count: Optional[int] = FieldInfo(alias="itemClassCount", default=None)

    item_class_offset: Optional[int] = FieldInfo(alias="itemClassOffset", default=None)

    item_offset: Optional[int] = FieldInfo(alias="itemOffset", default=None)

    item_reference_id: Optional[str] = FieldInfo(alias="itemReferenceID", default=None)

    page_end: Optional[int] = FieldInfo(alias="pageEnd", default=None)

    page_start: Optional[int] = FieldInfo(alias="pageStart", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)


class SplitCollectionEventSemanticPageOutput(BaseModel):
    item_count: Optional[int] = FieldInfo(alias="itemCount", default=None)

    items: Optional[List[SplitCollectionEventSemanticPageOutputItem]] = None

    page_count: Optional[int] = FieldInfo(alias="pageCount", default=None)


class SplitCollectionEvent(EventBase):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """
    Unique identifier of action type configuration that this event is associated
    with.
    """

    output_type: Literal["print_page", "semantic_page"] = FieldInfo(alias="outputType")

    print_page_output: SplitCollectionEventPrintPageOutput = FieldInfo(alias="printPageOutput")

    semantic_page_output: SplitCollectionEventSemanticPageOutput = FieldInfo(alias="semanticPageOutput")

    event_type: Optional[Literal["split_collection"]] = FieldInfo(alias="eventType", default=None)


class SplitItemEventPrintPageOutput(BaseModel):
    collection_reference_id: Optional[str] = FieldInfo(alias="collectionReferenceID", default=None)

    item_count: Optional[int] = FieldInfo(alias="itemCount", default=None)

    item_offset: Optional[int] = FieldInfo(alias="itemOffset", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)
    """The presigned S3 URL of the file that was split."""


class SplitItemEventSemanticPageOutput(BaseModel):
    collection_reference_id: Optional[str] = FieldInfo(alias="collectionReferenceID", default=None)

    item_class: Optional[str] = FieldInfo(alias="itemClass", default=None)

    item_class_count: Optional[int] = FieldInfo(alias="itemClassCount", default=None)

    item_class_offset: Optional[int] = FieldInfo(alias="itemClassOffset", default=None)

    item_count: Optional[int] = FieldInfo(alias="itemCount", default=None)

    item_offset: Optional[int] = FieldInfo(alias="itemOffset", default=None)

    page_count: Optional[int] = FieldInfo(alias="pageCount", default=None)

    page_end: Optional[int] = FieldInfo(alias="pageEnd", default=None)

    page_start: Optional[int] = FieldInfo(alias="pageStart", default=None)

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)


class SplitItemEvent(EventBase):
    output_type: Literal["print_page", "semantic_page"] = FieldInfo(alias="outputType")

    print_page_output: Optional[SplitItemEventPrintPageOutput] = FieldInfo(alias="printPageOutput", default=None)

    semantic_page_output: Optional[SplitItemEventSemanticPageOutput] = FieldInfo(
        alias="semanticPageOutput", default=None
    )


class ErrorEvent(EventBase):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """
    Unique identifier of action type configuration that this event is associated
    with.
    """

    message: str
    """Error message."""

    event_type: Optional[Literal["error"]] = FieldInfo(alias="eventType", default=None)


class JoinEventItem(BaseModel):
    item_count: int = FieldInfo(alias="itemCount")
    """The number of items that were transformed."""

    item_offset: int = FieldInfo(alias="itemOffset")
    """The offset of the first item that was transformed.

    Used for batch transformations to indicate which item in the batch this event
    corresponds to.
    """

    item_reference_id: str = FieldInfo(alias="itemReferenceID")
    """The unique ID you use internally to refer to this data point."""

    s3_url: Optional[str] = FieldInfo(alias="s3URL", default=None)
    """The presigned S3 URL of the file that was joined."""


class JoinEvent(EventBase):
    action_type_config_id: str = FieldInfo(alias="actionTypeConfigID")
    """
    Unique identifier of action type configuration that this event is associated
    with.
    """

    invalid_properties: List[str] = FieldInfo(alias="invalidProperties")
    """List of properties that were invalid in the input."""

    items: List[JoinEventItem]
    """The items that were joined."""

    join_type: Literal["standard"] = FieldInfo(alias="joinType")
    """The type of join that was performed."""

    transformed_content: object = FieldInfo(alias="transformedContent")
    """The transformed content of the input.

    The structure of this object is defined by the action type configuration.
    """

    event_type: Optional[Literal["join"]] = FieldInfo(alias="eventType", default=None)


Event: TypeAlias = Union[TransformEvent, RouteEvent, SplitCollectionEvent, SplitItemEvent, ErrorEvent, JoinEvent]
