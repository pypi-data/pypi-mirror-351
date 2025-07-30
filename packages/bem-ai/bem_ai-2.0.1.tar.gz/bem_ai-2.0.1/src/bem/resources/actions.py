# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Mapping, Iterable, cast
from typing_extensions import Literal, overload

import httpx

from ..types import ActionType, action_list_params, action_create_params, action_correct_route_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import extract_files, required_args, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.action_type import ActionType
from ..types.get_actions_response import GetActionsResponse

__all__ = ["ActionsResource", "AsyncActionsResource"]


class ActionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return ActionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateTransformActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateRouteActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateSplitActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateJoinActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        action_type: ActionType,
        action_type_config_id: str,
        actions: Iterable[action_create_params.CreateEmailActionsAction] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["actions", "action_type", "action_type_config_id"], ["action_type", "action_type_config_id"])
    def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateTransformActionsAction]
        | Iterable[action_create_params.CreateRouteActionsAction]
        | Iterable[action_create_params.CreateSplitActionsAction]
        | Iterable[action_create_params.CreateJoinActionsAction]
        | Iterable[action_create_params.CreateEmailActionsAction]
        | NotGiven = NOT_GIVEN,
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        body = deepcopy_minimal(
            {
                "actions": actions,
                "action_type": action_type,
                "action_type_config_id": action_type_config_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"], ["files", "<array>"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v1-alpha/actions",
            body=maybe_transform(body, action_create_params.ActionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetActionsResponse,
        )

    def list(
        self,
        *,
        action_ids: List[str] | NotGiven = NOT_GIVEN,
        action_type: ActionType | NotGiven = NOT_GIVEN,
        action_type_config_ids: List[str] | NotGiven = NOT_GIVEN,
        ending_before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        starting_after: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        List Actions

        Args:
          action_type: The type of the action.

          ending_before: A cursor to use in pagination. `endingBefore` is an action ID that defines your
              place in the list.

          sort_order: Specifies sorting behavior. The two options are `asc` and `desc` to sort
              ascending and descending respectively, with default sort being ascending. Paging
              works in both directions.

          starting_after: A cursor to use in pagination. `startingAfter` is an action ID that defines your
              place in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1-alpha/actions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "action_ids": action_ids,
                        "action_type": action_type,
                        "action_type_config_ids": action_type_config_ids,
                        "ending_before": ending_before,
                        "limit": limit,
                        "sort_order": sort_order,
                        "starting_after": starting_after,
                    },
                    action_list_params.ActionListParams,
                ),
            ),
            cast_to=GetActionsResponse,
        )

    def correct_route(
        self,
        *,
        route_actions: Iterable[action_correct_route_params.RouteAction] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Updates a route event with feedback on the desired router choices.

        Args:
          route_actions: An array of objects containing all the route actions you want to submit feedback
              for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._patch(
            "/v1-alpha/actions/route",
            body=maybe_transform(
                {"route_actions": route_actions}, action_correct_route_params.ActionCorrectRouteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncActionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncActionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return AsyncActionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateTransformActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateRouteActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateSplitActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateJoinActionsAction],
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        action_type: ActionType,
        action_type_config_id: str,
        actions: Iterable[action_create_params.CreateEmailActionsAction] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        Create a batch of Actions

        Args:
          action_type: The type of the action.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["actions", "action_type", "action_type_config_id"], ["action_type", "action_type_config_id"])
    async def create(
        self,
        *,
        actions: Iterable[action_create_params.CreateTransformActionsAction]
        | Iterable[action_create_params.CreateRouteActionsAction]
        | Iterable[action_create_params.CreateSplitActionsAction]
        | Iterable[action_create_params.CreateJoinActionsAction]
        | Iterable[action_create_params.CreateEmailActionsAction]
        | NotGiven = NOT_GIVEN,
        action_type: ActionType,
        action_type_config_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        body = deepcopy_minimal(
            {
                "actions": actions,
                "action_type": action_type,
                "action_type_config_id": action_type_config_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"], ["files", "<array>"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v1-alpha/actions",
            body=await async_maybe_transform(body, action_create_params.ActionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GetActionsResponse,
        )

    async def list(
        self,
        *,
        action_ids: List[str] | NotGiven = NOT_GIVEN,
        action_type: ActionType | NotGiven = NOT_GIVEN,
        action_type_config_ids: List[str] | NotGiven = NOT_GIVEN,
        ending_before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort_order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        starting_after: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GetActionsResponse:
        """
        List Actions

        Args:
          action_type: The type of the action.

          ending_before: A cursor to use in pagination. `endingBefore` is an action ID that defines your
              place in the list.

          sort_order: Specifies sorting behavior. The two options are `asc` and `desc` to sort
              ascending and descending respectively, with default sort being ascending. Paging
              works in both directions.

          starting_after: A cursor to use in pagination. `startingAfter` is an action ID that defines your
              place in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1-alpha/actions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "action_ids": action_ids,
                        "action_type": action_type,
                        "action_type_config_ids": action_type_config_ids,
                        "ending_before": ending_before,
                        "limit": limit,
                        "sort_order": sort_order,
                        "starting_after": starting_after,
                    },
                    action_list_params.ActionListParams,
                ),
            ),
            cast_to=GetActionsResponse,
        )

    async def correct_route(
        self,
        *,
        route_actions: Iterable[action_correct_route_params.RouteAction] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Updates a route event with feedback on the desired router choices.

        Args:
          route_actions: An array of objects containing all the route actions you want to submit feedback
              for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._patch(
            "/v1-alpha/actions/route",
            body=await async_maybe_transform(
                {"route_actions": route_actions}, action_correct_route_params.ActionCorrectRouteParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ActionsResourceWithRawResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.create = to_raw_response_wrapper(
            actions.create,
        )
        self.list = to_raw_response_wrapper(
            actions.list,
        )
        self.correct_route = to_raw_response_wrapper(
            actions.correct_route,
        )


class AsyncActionsResourceWithRawResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.create = async_to_raw_response_wrapper(
            actions.create,
        )
        self.list = async_to_raw_response_wrapper(
            actions.list,
        )
        self.correct_route = async_to_raw_response_wrapper(
            actions.correct_route,
        )


class ActionsResourceWithStreamingResponse:
    def __init__(self, actions: ActionsResource) -> None:
        self._actions = actions

        self.create = to_streamed_response_wrapper(
            actions.create,
        )
        self.list = to_streamed_response_wrapper(
            actions.list,
        )
        self.correct_route = to_streamed_response_wrapper(
            actions.correct_route,
        )


class AsyncActionsResourceWithStreamingResponse:
    def __init__(self, actions: AsyncActionsResource) -> None:
        self._actions = actions

        self.create = async_to_streamed_response_wrapper(
            actions.create,
        )
        self.list = async_to_streamed_response_wrapper(
            actions.list,
        )
        self.correct_route = async_to_streamed_response_wrapper(
            actions.correct_route,
        )
