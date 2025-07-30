# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .action_base import ActionBase
from .join_action_base import JoinActionBase
from .email_action_base import EmailActionBase
from .route_action_base import RouteActionBase
from .split_action_base import SplitActionBase
from .transform_action_base import TransformActionBase

__all__ = [
    "GetActionsResponse",
    "ActionTransformAction",
    "ActionRouteAction",
    "ActionSplitAction",
    "ActionJoinAction",
    "ActionEmailAction",
]


class ActionTransformAction(ActionBase, TransformActionBase):
    action_type: Literal["transform"] = FieldInfo(alias="actionType")


class ActionRouteAction(ActionBase, RouteActionBase):
    action_type: Literal["route"] = FieldInfo(alias="actionType")


class ActionSplitAction(ActionBase, SplitActionBase):
    action_type: Literal["split"] = FieldInfo(alias="actionType")


class ActionJoinAction(ActionBase, JoinActionBase):
    action_type: Literal["join"] = FieldInfo(alias="actionType")


class ActionEmailAction(ActionBase, EmailActionBase):
    action_type: Literal["email"] = FieldInfo(alias="actionType")


class GetActionsResponse(BaseModel):
    actions: Optional[
        List[Union[ActionTransformAction, ActionRouteAction, ActionSplitAction, ActionJoinAction, ActionEmailAction]]
    ] = None
