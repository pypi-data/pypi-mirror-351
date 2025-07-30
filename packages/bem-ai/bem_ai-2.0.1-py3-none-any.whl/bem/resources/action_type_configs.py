# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Iterable, cast
from typing_extensions import Literal, overload

import httpx

from ..types import (
    ActionType,
    action_type_config_list_params,
    action_type_config_create_params,
    action_type_config_update_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import required_args, maybe_transform, async_maybe_transform
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
from ..types.action_type_config import ActionTypeConfig
from ..types.route_list_item_param import RouteListItemParam
from ..types.action_type_config_list_response import ActionTypeConfigListResponse

__all__ = ["ActionTypeConfigsResource", "AsyncActionTypeConfigsResource"]


class ActionTypeConfigsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActionTypeConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ActionTypeConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActionTypeConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return ActionTypeConfigsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        body: action_type_config_create_params.CreateTransformConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateRouteConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateSplitConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateJoinConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateEmailConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["body"])
    def create(
        self,
        *,
        body: action_type_config_create_params.CreateTransformConfigBody
        | action_type_config_create_params.CreateRouteConfigBody
        | action_type_config_create_params.CreateSplitConfigBody
        | action_type_config_create_params.CreateJoinConfigBody
        | action_type_config_create_params.CreateEmailConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        return cast(
            ActionTypeConfig,
            self._post(
                "/v1-alpha/action-type-configs",
                body=maybe_transform(body, action_type_config_create_params.ActionTypeConfigCreateParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def retrieve(
        self,
        action_type_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Get an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        return cast(
            ActionTypeConfig,
            self._get(
                f"/v1-alpha/action-type-configs/{action_type_config_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    def update(
        self,
        action_type_config_id: str,
        *,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          next_action_type_config_id: Unique identifier of action type config to run after transformation. Currently
              only email is supported.

          output_schema: Desired output structure defined in standard JSON Schema convention.

          output_schema_name: Name of output schema object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def update(
        self,
        action_type_config_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        routes: Iterable[RouteListItemParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """Update an Action Type Config

        Args:
          description: Description of router.

        Can be used to provide additional context on router's
              purpose and expected inputs.

          routes: List of routes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def update(
        self,
        action_type_config_id: str,
        *,
        name: str | NotGiven = NOT_GIVEN,
        print_page_split_config: action_type_config_update_params.UpsertSplitConfigPrintPageSplitConfig
        | NotGiven = NOT_GIVEN,
        semantic_page_split_config: action_type_config_update_params.UpsertSplitConfigSemanticPageSplitConfig
        | NotGiven = NOT_GIVEN,
        split_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def update(
        self,
        action_type_config_id: str,
        *,
        join_type: Literal["standard"] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          join_type: The type of join to perform.

          next_action_type_config_id: Unique identifier of action type config to run after join.

          output_schema: Desired output structure defined in standard JSON Schema convention.

          output_schema_name: Name of output schema object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def update(
        self,
        action_type_config_id: str,
        *,
        body: str | NotGiven = NOT_GIVEN,
        from_email: str | NotGiven = NOT_GIVEN,
        from_name: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        to_email: str | NotGiven = NOT_GIVEN,
        to_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """Update an Action Type Config

        Args:
          body: Body of the email.

        This can be HTML, and include template variables in the form
              of `{{template_variable}}`. Template variables are taken from the output of the
              transformation.

          from_email: Email address to send the email from.

          from_name: Name of the sender.

          subject: Subject of the email. This can include template variables in the form of
              `{{template_variable}}`. Template variables are taken from the output of the
              transformation.

          to_email: Email address to send the email to.

          to_name: Name of the recipient.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def update(
        self,
        action_type_config_id: str,
        *,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        routes: Iterable[RouteListItemParam] | NotGiven = NOT_GIVEN,
        print_page_split_config: action_type_config_update_params.UpsertSplitConfigPrintPageSplitConfig
        | NotGiven = NOT_GIVEN,
        semantic_page_split_config: action_type_config_update_params.UpsertSplitConfigSemanticPageSplitConfig
        | NotGiven = NOT_GIVEN,
        split_type: str | NotGiven = NOT_GIVEN,
        join_type: Literal["standard"] | NotGiven = NOT_GIVEN,
        body: str | NotGiven = NOT_GIVEN,
        from_email: str | NotGiven = NOT_GIVEN,
        from_name: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        to_email: str | NotGiven = NOT_GIVEN,
        to_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        return cast(
            ActionTypeConfig,
            self._patch(
                f"/v1-alpha/action-type-configs/{action_type_config_id}",
                body=maybe_transform(
                    {
                        "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                        "independent_document_processing_enabled": independent_document_processing_enabled,
                        "name": name,
                        "next_action_type_config_id": next_action_type_config_id,
                        "output_schema": output_schema,
                        "output_schema_name": output_schema_name,
                        "description": description,
                        "routes": routes,
                        "print_page_split_config": print_page_split_config,
                        "semantic_page_split_config": semantic_page_split_config,
                        "split_type": split_type,
                        "join_type": join_type,
                        "body": body,
                        "from_email": from_email,
                        "from_name": from_name,
                        "subject": subject,
                        "to_email": to_email,
                        "to_name": to_name,
                    },
                    action_type_config_update_params.ActionTypeConfigUpdateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
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
    ) -> ActionTypeConfigListResponse:
        """
        List Action Type Configs

        Args:
          action_type: The type of the action.

          ending_before: A cursor to use in pagination. `endingBefore` is an action type config ID that
              defines your place in the list.

          sort_order: Specifies sorting behavior. The two options are `asc` and `desc` to sort
              ascending and descending respectively, with default sort being ascending. Paging
              works in both directions.

          starting_after: A cursor to use in pagination. `startingAfter` is an action type config ID that
              defines your place in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1-alpha/action-type-configs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "action_type": action_type,
                        "action_type_config_ids": action_type_config_ids,
                        "ending_before": ending_before,
                        "limit": limit,
                        "sort_order": sort_order,
                        "starting_after": starting_after,
                    },
                    action_type_config_list_params.ActionTypeConfigListParams,
                ),
            ),
            cast_to=ActionTypeConfigListResponse,
        )

    def delete(
        self,
        action_type_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1-alpha/action-type-configs/{action_type_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncActionTypeConfigsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActionTypeConfigsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncActionTypeConfigsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActionTypeConfigsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return AsyncActionTypeConfigsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        body: action_type_config_create_params.CreateTransformConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateRouteConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateSplitConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateJoinConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
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
        body: action_type_config_create_params.CreateEmailConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Create an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["body"])
    async def create(
        self,
        *,
        body: action_type_config_create_params.CreateTransformConfigBody
        | action_type_config_create_params.CreateRouteConfigBody
        | action_type_config_create_params.CreateSplitConfigBody
        | action_type_config_create_params.CreateJoinConfigBody
        | action_type_config_create_params.CreateEmailConfigBody,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        return cast(
            ActionTypeConfig,
            await self._post(
                "/v1-alpha/action-type-configs",
                body=await async_maybe_transform(body, action_type_config_create_params.ActionTypeConfigCreateParams),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def retrieve(
        self,
        action_type_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Get an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        return cast(
            ActionTypeConfig,
            await self._get(
                f"/v1-alpha/action-type-configs/{action_type_config_id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    @overload
    async def update(
        self,
        action_type_config_id: str,
        *,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          next_action_type_config_id: Unique identifier of action type config to run after transformation. Currently
              only email is supported.

          output_schema: Desired output structure defined in standard JSON Schema convention.

          output_schema_name: Name of output schema object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def update(
        self,
        action_type_config_id: str,
        *,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        routes: Iterable[RouteListItemParam] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """Update an Action Type Config

        Args:
          description: Description of router.

        Can be used to provide additional context on router's
              purpose and expected inputs.

          routes: List of routes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def update(
        self,
        action_type_config_id: str,
        *,
        name: str | NotGiven = NOT_GIVEN,
        print_page_split_config: action_type_config_update_params.UpsertSplitConfigPrintPageSplitConfig
        | NotGiven = NOT_GIVEN,
        semantic_page_split_config: action_type_config_update_params.UpsertSplitConfigSemanticPageSplitConfig
        | NotGiven = NOT_GIVEN,
        split_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def update(
        self,
        action_type_config_id: str,
        *,
        join_type: Literal["standard"] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """
        Update an Action Type Config

        Args:
          join_type: The type of join to perform.

          next_action_type_config_id: Unique identifier of action type config to run after join.

          output_schema: Desired output structure defined in standard JSON Schema convention.

          output_schema_name: Name of output schema object.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def update(
        self,
        action_type_config_id: str,
        *,
        body: str | NotGiven = NOT_GIVEN,
        from_email: str | NotGiven = NOT_GIVEN,
        from_name: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        to_email: str | NotGiven = NOT_GIVEN,
        to_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        """Update an Action Type Config

        Args:
          body: Body of the email.

        This can be HTML, and include template variables in the form
              of `{{template_variable}}`. Template variables are taken from the output of the
              transformation.

          from_email: Email address to send the email from.

          from_name: Name of the sender.

          subject: Subject of the email. This can include template variables in the form of
              `{{template_variable}}`. Template variables are taken from the output of the
              transformation.

          to_email: Email address to send the email to.

          to_name: Name of the recipient.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def update(
        self,
        action_type_config_id: str,
        *,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        next_action_type_config_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        routes: Iterable[RouteListItemParam] | NotGiven = NOT_GIVEN,
        print_page_split_config: action_type_config_update_params.UpsertSplitConfigPrintPageSplitConfig
        | NotGiven = NOT_GIVEN,
        semantic_page_split_config: action_type_config_update_params.UpsertSplitConfigSemanticPageSplitConfig
        | NotGiven = NOT_GIVEN,
        split_type: str | NotGiven = NOT_GIVEN,
        join_type: Literal["standard"] | NotGiven = NOT_GIVEN,
        body: str | NotGiven = NOT_GIVEN,
        from_email: str | NotGiven = NOT_GIVEN,
        from_name: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        to_email: str | NotGiven = NOT_GIVEN,
        to_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ActionTypeConfig:
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        return cast(
            ActionTypeConfig,
            await self._patch(
                f"/v1-alpha/action-type-configs/{action_type_config_id}",
                body=await async_maybe_transform(
                    {
                        "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                        "independent_document_processing_enabled": independent_document_processing_enabled,
                        "name": name,
                        "next_action_type_config_id": next_action_type_config_id,
                        "output_schema": output_schema,
                        "output_schema_name": output_schema_name,
                        "description": description,
                        "routes": routes,
                        "print_page_split_config": print_page_split_config,
                        "semantic_page_split_config": semantic_page_split_config,
                        "split_type": split_type,
                        "join_type": join_type,
                        "body": body,
                        "from_email": from_email,
                        "from_name": from_name,
                        "subject": subject,
                        "to_email": to_email,
                        "to_name": to_name,
                    },
                    action_type_config_update_params.ActionTypeConfigUpdateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(Any, ActionTypeConfig),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list(
        self,
        *,
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
    ) -> ActionTypeConfigListResponse:
        """
        List Action Type Configs

        Args:
          action_type: The type of the action.

          ending_before: A cursor to use in pagination. `endingBefore` is an action type config ID that
              defines your place in the list.

          sort_order: Specifies sorting behavior. The two options are `asc` and `desc` to sort
              ascending and descending respectively, with default sort being ascending. Paging
              works in both directions.

          starting_after: A cursor to use in pagination. `startingAfter` is an action type config ID that
              defines your place in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1-alpha/action-type-configs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "action_type": action_type,
                        "action_type_config_ids": action_type_config_ids,
                        "ending_before": ending_before,
                        "limit": limit,
                        "sort_order": sort_order,
                        "starting_after": starting_after,
                    },
                    action_type_config_list_params.ActionTypeConfigListParams,
                ),
            ),
            cast_to=ActionTypeConfigListResponse,
        )

    async def delete(
        self,
        action_type_config_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete an Action Type Config

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not action_type_config_id:
            raise ValueError(
                f"Expected a non-empty value for `action_type_config_id` but received {action_type_config_id!r}"
            )
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1-alpha/action-type-configs/{action_type_config_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ActionTypeConfigsResourceWithRawResponse:
    def __init__(self, action_type_configs: ActionTypeConfigsResource) -> None:
        self._action_type_configs = action_type_configs

        self.create = to_raw_response_wrapper(
            action_type_configs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            action_type_configs.retrieve,
        )
        self.update = to_raw_response_wrapper(
            action_type_configs.update,
        )
        self.list = to_raw_response_wrapper(
            action_type_configs.list,
        )
        self.delete = to_raw_response_wrapper(
            action_type_configs.delete,
        )


class AsyncActionTypeConfigsResourceWithRawResponse:
    def __init__(self, action_type_configs: AsyncActionTypeConfigsResource) -> None:
        self._action_type_configs = action_type_configs

        self.create = async_to_raw_response_wrapper(
            action_type_configs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            action_type_configs.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            action_type_configs.update,
        )
        self.list = async_to_raw_response_wrapper(
            action_type_configs.list,
        )
        self.delete = async_to_raw_response_wrapper(
            action_type_configs.delete,
        )


class ActionTypeConfigsResourceWithStreamingResponse:
    def __init__(self, action_type_configs: ActionTypeConfigsResource) -> None:
        self._action_type_configs = action_type_configs

        self.create = to_streamed_response_wrapper(
            action_type_configs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            action_type_configs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            action_type_configs.update,
        )
        self.list = to_streamed_response_wrapper(
            action_type_configs.list,
        )
        self.delete = to_streamed_response_wrapper(
            action_type_configs.delete,
        )


class AsyncActionTypeConfigsResourceWithStreamingResponse:
    def __init__(self, action_type_configs: AsyncActionTypeConfigsResource) -> None:
        self._action_type_configs = action_type_configs

        self.create = async_to_streamed_response_wrapper(
            action_type_configs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            action_type_configs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            action_type_configs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            action_type_configs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            action_type_configs.delete,
        )
