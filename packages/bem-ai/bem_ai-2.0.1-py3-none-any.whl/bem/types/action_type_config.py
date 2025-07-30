# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from .._utils import PropertyInfo
from .._models import BaseModel
from .route_list_item import RouteListItem
from .action_type_config_base import ActionTypeConfigBase
from .split_config_semantic_page_item_class import SplitConfigSemanticPageItemClass

__all__ = [
    "ActionTypeConfig",
    "TransformConfig",
    "RouteConfig",
    "SplitConfig",
    "SplitConfigPrintPageSplitConfig",
    "SplitConfigSemanticPageSplitConfig",
    "JoinConfig",
    "EmailConfig",
]


class TransformConfig(ActionTypeConfigBase):
    action_type: Literal["transform"] = FieldInfo(alias="actionType")

    complex_tabular_transform_enabled: bool = FieldInfo(alias="complexTabularTransformEnabled")
    """Whether complex tabular transforms are enabled on the pipeline.

    This enables the pipeline to parse CSVs with multiple tables in the same file,
    and to transpose CSVs that can't be parsed row-wise.
    """

    email_address: str = FieldInfo(alias="emailAddress")
    """Email address automatically created by bem.

    You can forward emails with or without attachments, to be transformed.
    """

    independent_document_processing_enabled: bool = FieldInfo(alias="independentDocumentProcessingEnabled")
    """Whether independent transformations is enabled.

    For PDFs sent through the pipeline, this enables independent transformations for
    each individual page. For CSVs, this enables transforming chunks of rows in the
    CSV.
    """

    output_schema: object = FieldInfo(alias="outputSchema")
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: str = FieldInfo(alias="outputSchemaName")
    """Name of output schema object."""

    next_action_type_config_id: Optional[str] = FieldInfo(alias="nextActionTypeConfigID", default=None)
    """Unique identifier of action type config to run after transformation.

    Currently only email is supported.
    """


class RouteConfig(ActionTypeConfigBase):
    action_type: Literal["route"] = FieldInfo(alias="actionType")

    routes: List[RouteListItem]
    """List of routes."""

    description: Optional[str] = None
    """Description of router.

    Can be used to provide additional context on router's purpose and expected
    inputs.
    """

    email_address: Optional[str] = FieldInfo(alias="emailAddress", default=None)
    """Email address automatically created by bem.

    You can forward emails with or without attachments, to be routed.
    """


class SplitConfigPrintPageSplitConfig(BaseModel):
    next_action_type_config_id: Optional[str] = FieldInfo(alias="nextActionTypeConfigID", default=None)
    """The unique ID of the action type configuration you want to use for this action."""


class SplitConfigSemanticPageSplitConfig(BaseModel):
    item_classes: Optional[List[SplitConfigSemanticPageItemClass]] = FieldInfo(alias="itemClasses", default=None)


class SplitConfig(ActionTypeConfigBase):
    action_type: Literal["split"] = FieldInfo(alias="actionType")

    split_type: Literal["print_page", "semantic_page"] = FieldInfo(alias="splitType")

    print_page_split_config: Optional[SplitConfigPrintPageSplitConfig] = FieldInfo(
        alias="printPageSplitConfig", default=None
    )

    semantic_page_split_config: Optional[SplitConfigSemanticPageSplitConfig] = FieldInfo(
        alias="semanticPageSplitConfig", default=None
    )


class JoinConfig(ActionTypeConfigBase):
    action_type: Literal["join"] = FieldInfo(alias="actionType")

    output_schema: object = FieldInfo(alias="outputSchema")
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: str = FieldInfo(alias="outputSchemaName")
    """Name of output schema object."""

    join_type: Optional[Literal["standard"]] = FieldInfo(alias="joinType", default=None)
    """The type of join to perform."""

    next_action_type_config_id: Optional[str] = FieldInfo(alias="nextActionTypeConfigID", default=None)
    """Unique identifier of action type config to run after join."""


class EmailConfig(ActionTypeConfigBase):
    action_type: Literal["email"] = FieldInfo(alias="actionType")

    body: str
    """Body of the email.

    This can be HTML, and include template variables in the form of
    `{{template_variable}}`. Template variables are taken from the output of the
    transformation.
    """

    from_email: str = FieldInfo(alias="fromEmail")
    """Email address to send the email from."""

    from_name: str = FieldInfo(alias="fromName")
    """Name of the sender."""

    subject: str
    """Subject of the email.

    This can include template variables in the form of `{{template_variable}}`.
    Template variables are taken from the output of the transformation.
    """

    to_email: str = FieldInfo(alias="toEmail")
    """Email address to send the email to."""

    to_name: str = FieldInfo(alias="toName")
    """Name of the recipient."""


ActionTypeConfig: TypeAlias = Annotated[
    Union[TransformConfig, RouteConfig, SplitConfig, JoinConfig, EmailConfig], PropertyInfo(discriminator="action_type")
]
