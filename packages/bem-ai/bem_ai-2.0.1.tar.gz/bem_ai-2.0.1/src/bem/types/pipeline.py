# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .action_type_config import ActionTypeConfig

__all__ = ["Pipeline"]


class Pipeline(BaseModel):
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

    name: str
    """Name of pipeline"""

    output_schema: object = FieldInfo(alias="outputSchema")
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: str = FieldInfo(alias="outputSchemaName")
    """Name of output schema object."""

    pipeline_id: str = FieldInfo(alias="pipelineID")
    """The unique identifier of the pipeline."""

    action_config: Optional[ActionTypeConfig] = FieldInfo(alias="actionConfig", default=None)
    """
    Configuration of router that maps names of routes to respective pipelines to
    route to.
    """

    webhook_enabled: Optional[bool] = FieldInfo(alias="webhookEnabled", default=None)
    """DEPRECATED - use subscriptions for webhook events.

    Whether webhook functionality is enabled.
    """

    webhook_url: Optional[str] = FieldInfo(alias="webhookURL", default=None)
    """DEPRECATED - use subscriptions for webhook events.

    URL bem will send webhook requests to if webhooks are enabled for the pipeline.
    """
