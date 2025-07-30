# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated

from .._utils import PropertyInfo
from .action_type_config_upsert_base_param import ActionTypeConfigUpsertBaseParam

__all__ = ["UpsertJoinConfigParam"]


class UpsertJoinConfigParam(ActionTypeConfigUpsertBaseParam, total=False):
    join_type: Annotated[Literal["standard"], PropertyInfo(alias="joinType")]
    """The type of join to perform."""

    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """Unique identifier of action type config to run after join."""

    output_schema: Annotated[object, PropertyInfo(alias="outputSchema")]
    """Desired output structure defined in standard JSON Schema convention."""

    output_schema_name: Annotated[str, PropertyInfo(alias="outputSchemaName")]
    """Name of output schema object."""
