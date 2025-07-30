# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .action_type import ActionType
from .join_action_base_param import JoinActionBaseParam
from .email_action_base_param import EmailActionBaseParam
from .route_action_base_param import RouteActionBaseParam
from .split_action_base_param import SplitActionBaseParam
from .create_action_base_param import CreateActionBaseParam
from .transform_action_base_param import TransformActionBaseParam

__all__ = [
    "ActionCreateParams",
    "CreateTransformActions",
    "CreateTransformActionsAction",
    "CreateRouteActions",
    "CreateRouteActionsAction",
    "CreateSplitActions",
    "CreateSplitActionsAction",
    "CreateJoinActions",
    "CreateJoinActionsAction",
    "CreateEmailActions",
    "CreateEmailActionsAction",
]


class CreateTransformActions(TypedDict, total=False):
    actions: Required[Iterable[CreateTransformActionsAction]]

    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""

    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]


class CreateTransformActionsAction(CreateActionBaseParam, TransformActionBaseParam, total=False):
    pass


class CreateRouteActions(TypedDict, total=False):
    actions: Required[Iterable[CreateRouteActionsAction]]

    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""

    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]


class CreateRouteActionsAction(CreateActionBaseParam, RouteActionBaseParam, total=False):
    pass


class CreateSplitActions(TypedDict, total=False):
    actions: Required[Iterable[CreateSplitActionsAction]]

    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""

    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]


class CreateSplitActionsAction(CreateActionBaseParam, SplitActionBaseParam, total=False):
    pass


class CreateJoinActions(TypedDict, total=False):
    actions: Required[Iterable[CreateJoinActionsAction]]

    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""

    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]


class CreateJoinActionsAction(CreateActionBaseParam, JoinActionBaseParam, total=False):
    pass


class CreateEmailActions(TypedDict, total=False):
    action_type: Required[Annotated[ActionType, PropertyInfo(alias="actionType")]]
    """The type of the action."""

    action_type_config_id: Required[Annotated[str, PropertyInfo(alias="actionTypeConfigID")]]

    actions: Iterable[CreateEmailActionsAction]


class CreateEmailActionsAction(CreateActionBaseParam, EmailActionBaseParam, total=False):
    pass


ActionCreateParams: TypeAlias = Union[
    CreateTransformActions, CreateRouteActions, CreateSplitActions, CreateJoinActions, CreateEmailActions
]
