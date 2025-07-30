# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .route_list_item_param import RouteListItemParam
from .split_config_semantic_page_item_class_param import SplitConfigSemanticPageItemClassParam

__all__ = [
    "ActionTypeConfigUpdateParams",
    "UpsertTransformConfig",
    "UpsertRouteConfig",
    "UpsertSplitConfig",
    "UpsertSplitConfigPrintPageSplitConfig",
    "UpsertSplitConfigSemanticPageSplitConfig",
    "UpsertJoinConfig",
    "UpsertEmailConfig",
]


class UpsertTransformConfig(TypedDict, total=False):
    complex_tabular_transform_enabled: Annotated[bool, PropertyInfo(alias="complexTabularTransformEnabled")]
    """Whether complex tabular transforms are enabled on the pipeline.

    This enables the pipeline to parse CSVs with multiple tables in the same file,
    and to transpose CSVs that can't be parsed row-wise.
    """

    independent_document_processing_enabled: Annotated[bool, PropertyInfo(alias="independentDocumentProcessingEnabled")]
    """Whether independent transformations is enabled.

    For PDFs sent through the pipeline, this enables independent transformations for
    each individual page. For CSVs, this enables transforming chunks of rows in the
    CSV.
    """

    name: str

    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """Unique identifier of action type config to run after transformation.

    Currently only email is supported.
    """

    output_schema: Annotated[object, PropertyInfo(alias="outputSchema")]
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: Annotated[str, PropertyInfo(alias="outputSchemaName")]
    """Name of output schema object."""


class UpsertRouteConfig(TypedDict, total=False):
    description: str
    """Description of router.

    Can be used to provide additional context on router's purpose and expected
    inputs.
    """

    name: str

    routes: Iterable[RouteListItemParam]
    """List of routes."""


class UpsertSplitConfig(TypedDict, total=False):
    name: str

    print_page_split_config: Annotated[
        UpsertSplitConfigPrintPageSplitConfig, PropertyInfo(alias="printPageSplitConfig")
    ]

    semantic_page_split_config: Annotated[
        UpsertSplitConfigSemanticPageSplitConfig, PropertyInfo(alias="semanticPageSplitConfig")
    ]

    split_type: Annotated[str, PropertyInfo(alias="splitType")]


class UpsertSplitConfigPrintPageSplitConfig(TypedDict, total=False):
    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """The unique ID of the action type configuration you want to use for this action."""


class UpsertSplitConfigSemanticPageSplitConfig(TypedDict, total=False):
    item_classes: Annotated[Iterable[SplitConfigSemanticPageItemClassParam], PropertyInfo(alias="itemClasses")]


class UpsertJoinConfig(TypedDict, total=False):
    join_type: Annotated[Literal["standard"], PropertyInfo(alias="joinType")]
    """The type of join to perform."""

    name: str

    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """Unique identifier of action type config to run after join."""

    output_schema: Annotated[object, PropertyInfo(alias="outputSchema")]
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: Annotated[str, PropertyInfo(alias="outputSchemaName")]
    """Name of output schema object."""


class UpsertEmailConfig(TypedDict, total=False):
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

    name: str

    subject: str
    """Subject of the email.

    This can include template variables in the form of `{{template_variable}}`.
    Template variables are taken from the output of the transformation.
    """

    to_email: Annotated[str, PropertyInfo(alias="toEmail")]
    """Email address to send the email to."""

    to_name: Annotated[str, PropertyInfo(alias="toName")]
    """Name of the recipient."""


ActionTypeConfigUpdateParams: TypeAlias = Union[
    UpsertTransformConfig, UpsertRouteConfig, UpsertSplitConfig, UpsertJoinConfig, UpsertEmailConfig
]
