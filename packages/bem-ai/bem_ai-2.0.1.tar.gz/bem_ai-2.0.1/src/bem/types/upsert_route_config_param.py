# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

from .route_list_item_param import RouteListItemParam
from .action_type_config_upsert_base_param import ActionTypeConfigUpsertBaseParam

__all__ = ["UpsertRouteConfigParam"]


class UpsertRouteConfigParam(ActionTypeConfigUpsertBaseParam, total=False):
    description: str
    """Description of router.

    Can be used to provide additional context on router's purpose and expected
    inputs.
    """

    routes: Iterable[RouteListItemParam]
    """List of routes."""
