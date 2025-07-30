# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .action_type_config import ActionTypeConfig

__all__ = ["ActionTypeConfigListResponse"]


class ActionTypeConfigListResponse(BaseModel):
    action_type_configs: Optional[List[ActionTypeConfig]] = FieldInfo(alias="actionTypeConfigs", default=None)
