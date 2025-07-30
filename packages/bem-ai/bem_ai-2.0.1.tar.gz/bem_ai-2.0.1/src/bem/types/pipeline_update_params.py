# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .action_type_config_param import ActionTypeConfigParam

__all__ = ["PipelineUpdateParams"]


class PipelineUpdateParams(TypedDict, total=False):
    action_config: Annotated[ActionTypeConfigParam, PropertyInfo(alias="actionConfig")]
    """
    Configuration of router that maps names of routes to respective pipelines to
    route to.
    """

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
    """Name of pipeline"""

    output_schema: Annotated[object, PropertyInfo(alias="outputSchema")]
    """Desired output structure defined in standard JSON Schema convention.

    Note - We DO NOT support non-alphanumeric characters in names of fields.
    """

    output_schema_name: Annotated[str, PropertyInfo(alias="outputSchemaName")]
    """Name of output schema object."""

    webhook_enabled: Annotated[bool, PropertyInfo(alias="webhookEnabled")]
    """DEPRECATED - use subscriptions for webhook events.

    Whether webhook functionality is enabled.
    """

    webhook_url: Annotated[str, PropertyInfo(alias="webhookURL")]
    """DEPRECATED - use subscriptions for webhook events.

    URL bem will send webhook requests to with successful transformation outputs if
    webhooks are enabled for the pipeline.
    """
