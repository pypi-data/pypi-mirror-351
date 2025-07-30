# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .action_type_config_upsert_base_param import ActionTypeConfigUpsertBaseParam
from .split_config_semantic_page_item_class_param import SplitConfigSemanticPageItemClassParam

__all__ = [
    "UpsertSplitConfigParam",
    "UpsertSplitConfigParamPrintPageSplitConfig",
    "UpsertSplitConfigParamSemanticPageSplitConfig",
]


class UpsertSplitConfigParamPrintPageSplitConfig(TypedDict, total=False):
    next_action_type_config_id: Annotated[str, PropertyInfo(alias="nextActionTypeConfigID")]
    """The unique ID of the action type configuration you want to use for this action."""


class UpsertSplitConfigParamSemanticPageSplitConfig(TypedDict, total=False):
    item_classes: Annotated[Iterable[SplitConfigSemanticPageItemClassParam], PropertyInfo(alias="itemClasses")]


class UpsertSplitConfigParam(ActionTypeConfigUpsertBaseParam, total=False):
    print_page_split_config: Annotated[
        UpsertSplitConfigParamPrintPageSplitConfig, PropertyInfo(alias="printPageSplitConfig")
    ]

    semantic_page_split_config: Annotated[
        UpsertSplitConfigParamSemanticPageSplitConfig, PropertyInfo(alias="semanticPageSplitConfig")
    ]

    split_type: Annotated[str, PropertyInfo(alias="splitType")]
