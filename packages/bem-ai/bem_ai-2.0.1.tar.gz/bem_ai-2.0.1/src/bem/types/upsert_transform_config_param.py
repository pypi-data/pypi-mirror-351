# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated

from .._utils import PropertyInfo
from .action_type_config_upsert_base_param import ActionTypeConfigUpsertBaseParam

__all__ = ["UpsertTransformConfigParam"]


class UpsertTransformConfigParam(ActionTypeConfigUpsertBaseParam, total=False):
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

    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """Unique identifier of action type config to run after transformation.

    Currently only email is supported.
    """

    output_schema: Annotated[object, PropertyInfo(alias="outputSchema")]
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: Annotated[str, PropertyInfo(alias="outputSchemaName")]
    """Name of output schema object."""
