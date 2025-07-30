# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .upsert_join_config_param import UpsertJoinConfigParam
from .upsert_email_config_param import UpsertEmailConfigParam
from .upsert_route_config_param import UpsertRouteConfigParam
from .upsert_split_config_param import UpsertSplitConfigParam
from .upsert_transform_config_param import UpsertTransformConfigParam
from .action_type_config_create_base_param import ActionTypeConfigCreateBaseParam

__all__ = [
    "ActionTypeConfigCreateParams",
    "CreateTransformConfig",
    "CreateTransformConfigBody",
    "CreateRouteConfig",
    "CreateRouteConfigBody",
    "CreateSplitConfig",
    "CreateSplitConfigBody",
    "CreateJoinConfig",
    "CreateJoinConfigBody",
    "CreateEmailConfig",
    "CreateEmailConfigBody",
]


class CreateTransformConfig(TypedDict, total=False):
    body: Required[CreateTransformConfigBody]


class CreateTransformConfigBody(ActionTypeConfigCreateBaseParam, UpsertTransformConfigParam, total=False):
    pass


class CreateRouteConfig(TypedDict, total=False):
    body: Required[CreateRouteConfigBody]


class CreateRouteConfigBody(ActionTypeConfigCreateBaseParam, UpsertRouteConfigParam, total=False):
    pass


class CreateSplitConfig(TypedDict, total=False):
    body: Required[CreateSplitConfigBody]


class CreateSplitConfigBody(ActionTypeConfigCreateBaseParam, UpsertSplitConfigParam, total=False):
    pass


class CreateJoinConfig(TypedDict, total=False):
    body: Required[CreateJoinConfigBody]


class CreateJoinConfigBody(ActionTypeConfigCreateBaseParam, UpsertJoinConfigParam, total=False):
    pass


class CreateEmailConfig(TypedDict, total=False):
    body: Required[CreateEmailConfigBody]


class CreateEmailConfigBody(ActionTypeConfigCreateBaseParam, UpsertEmailConfigParam, total=False):
    pass


ActionTypeConfigCreateParams: TypeAlias = Union[
    CreateTransformConfig, CreateRouteConfig, CreateSplitConfig, CreateJoinConfig, CreateEmailConfig
]
