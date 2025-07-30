# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import pipeline_list_params, pipeline_create_params, pipeline_update_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.pipeline import Pipeline
from ..types.pipeline_list_response import PipelineListResponse
from ..types.action_type_config_param import ActionTypeConfigParam
from ..types.pipeline_retrieve_response import PipelineRetrieveResponse

__all__ = ["PipelinesResource", "AsyncPipelinesResource"]


class PipelinesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PipelinesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PipelinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PipelinesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return PipelinesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        output_schema: object,
        action_config: ActionTypeConfigParam | NotGiven = NOT_GIVEN,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        webhook_enabled: bool | NotGiven = NOT_GIVEN,
        webhook_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Pipeline:
        """Creates a new pipeline to transform data, given an output schema.

        It returns the
        created pipeline's details. Pipelines are long-lived, so we recommend you create
        them outside of your application loop and reuse them.

        Args:
          name: Name of pipeline

          output_schema: Desired output structure defined in standard JSON Schema convention. Note - We
              DO NOT support non-alphanumeric characters in names of fields.

          action_config: Configuration of router that maps names of routes to respective pipelines to
              route to.

          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          output_schema_name: Name of output schema object.

          webhook_enabled: DEPRECATED - use subscriptions for webhook events. Whether webhook functionality
              is enabled.

          webhook_url: DEPRECATED - use subscriptions for webhook events. URL bem will send webhook
              requests to with successful transformation outputs if webhooks are enabled for
              the pipeline.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1-beta/pipelines",
            body=maybe_transform(
                {
                    "name": name,
                    "output_schema": output_schema,
                    "action_config": action_config,
                    "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                    "independent_document_processing_enabled": independent_document_processing_enabled,
                    "output_schema_name": output_schema_name,
                    "webhook_enabled": webhook_enabled,
                    "webhook_url": webhook_url,
                },
                pipeline_create_params.PipelineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Pipeline,
        )

    def retrieve(
        self,
        pipeline_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PipelineRetrieveResponse:
        """
        Retrieves configuration of an existing pipeline.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        return self._get(
            f"/v1-beta/pipelines/{pipeline_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PipelineRetrieveResponse,
        )

    def update(
        self,
        pipeline_id: str,
        *,
        action_config: ActionTypeConfigParam | NotGiven = NOT_GIVEN,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        webhook_enabled: bool | NotGiven = NOT_GIVEN,
        webhook_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Pipeline:
        """Updates an existing pipeline.

        Follow conventional PATCH behavior, so only
        included fields will be updated.

        Args:
          action_config: Configuration of router that maps names of routes to respective pipelines to
              route to.

          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          name: Name of pipeline

          output_schema: Desired output structure defined in standard JSON Schema convention. Note - We
              DO NOT support non-alphanumeric characters in names of fields.

          output_schema_name: Name of output schema object.

          webhook_enabled: DEPRECATED - use subscriptions for webhook events. Whether webhook functionality
              is enabled.

          webhook_url: DEPRECATED - use subscriptions for webhook events. URL bem will send webhook
              requests to with successful transformation outputs if webhooks are enabled for
              the pipeline.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        return self._patch(
            f"/v1-beta/pipelines/{pipeline_id}",
            body=maybe_transform(
                {
                    "action_config": action_config,
                    "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                    "independent_document_processing_enabled": independent_document_processing_enabled,
                    "name": name,
                    "output_schema": output_schema,
                    "output_schema_name": output_schema_name,
                    "webhook_enabled": webhook_enabled,
                    "webhook_url": webhook_url,
                },
                pipeline_update_params.PipelineUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Pipeline,
        )

    def list(
        self,
        *,
        ending_before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        starting_after: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PipelineListResponse:
        """
        Retrieves configurations for all existing pipelines.

        Args:
          ending_before: A cursor to use in pagination. `endingBefore` is a pipeline ID that defines your
              place in the list. For example, if you make a list request and receive 50
              objects, starting with `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call
              can include `endingBefore=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the previous
              page of the list.

          starting_after: A cursor to use in pagination. `startingAfter` is a pipeline ID that defines
              your place in the list. For example, if you make a list request and receive 50
              objects, ending with `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can
              include `startingAfter=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the next page of
              the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1-beta/pipelines",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ending_before": ending_before,
                        "limit": limit,
                        "starting_after": starting_after,
                    },
                    pipeline_list_params.PipelineListParams,
                ),
            ),
            cast_to=PipelineListResponse,
        )

    def delete(
        self,
        pipeline_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes an existing pipeline and all related transformations.

        **IMPORTANT NOTE:** be sure you have exported any relevant transformations
        produced by the pipeline before deleting given they won't be accessible through
        our API after deleting the pipeline.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1-beta/pipelines/{pipeline_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncPipelinesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPipelinesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPipelinesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPipelinesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return AsyncPipelinesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        output_schema: object,
        action_config: ActionTypeConfigParam | NotGiven = NOT_GIVEN,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        webhook_enabled: bool | NotGiven = NOT_GIVEN,
        webhook_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Pipeline:
        """Creates a new pipeline to transform data, given an output schema.

        It returns the
        created pipeline's details. Pipelines are long-lived, so we recommend you create
        them outside of your application loop and reuse them.

        Args:
          name: Name of pipeline

          output_schema: Desired output structure defined in standard JSON Schema convention. Note - We
              DO NOT support non-alphanumeric characters in names of fields.

          action_config: Configuration of router that maps names of routes to respective pipelines to
              route to.

          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          output_schema_name: Name of output schema object.

          webhook_enabled: DEPRECATED - use subscriptions for webhook events. Whether webhook functionality
              is enabled.

          webhook_url: DEPRECATED - use subscriptions for webhook events. URL bem will send webhook
              requests to with successful transformation outputs if webhooks are enabled for
              the pipeline.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1-beta/pipelines",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "output_schema": output_schema,
                    "action_config": action_config,
                    "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                    "independent_document_processing_enabled": independent_document_processing_enabled,
                    "output_schema_name": output_schema_name,
                    "webhook_enabled": webhook_enabled,
                    "webhook_url": webhook_url,
                },
                pipeline_create_params.PipelineCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Pipeline,
        )

    async def retrieve(
        self,
        pipeline_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PipelineRetrieveResponse:
        """
        Retrieves configuration of an existing pipeline.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        return await self._get(
            f"/v1-beta/pipelines/{pipeline_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PipelineRetrieveResponse,
        )

    async def update(
        self,
        pipeline_id: str,
        *,
        action_config: ActionTypeConfigParam | NotGiven = NOT_GIVEN,
        complex_tabular_transform_enabled: bool | NotGiven = NOT_GIVEN,
        independent_document_processing_enabled: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        output_schema_name: str | NotGiven = NOT_GIVEN,
        webhook_enabled: bool | NotGiven = NOT_GIVEN,
        webhook_url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Pipeline:
        """Updates an existing pipeline.

        Follow conventional PATCH behavior, so only
        included fields will be updated.

        Args:
          action_config: Configuration of router that maps names of routes to respective pipelines to
              route to.

          complex_tabular_transform_enabled: Whether complex tabular transforms are enabled on the pipeline. This enables the
              pipeline to parse CSVs with multiple tables in the same file, and to transpose
              CSVs that can't be parsed row-wise.

          independent_document_processing_enabled: Whether independent transformations is enabled. For PDFs sent through the
              pipeline, this enables independent transformations for each individual page. For
              CSVs, this enables transforming chunks of rows in the CSV.

          name: Name of pipeline

          output_schema: Desired output structure defined in standard JSON Schema convention. Note - We
              DO NOT support non-alphanumeric characters in names of fields.

          output_schema_name: Name of output schema object.

          webhook_enabled: DEPRECATED - use subscriptions for webhook events. Whether webhook functionality
              is enabled.

          webhook_url: DEPRECATED - use subscriptions for webhook events. URL bem will send webhook
              requests to with successful transformation outputs if webhooks are enabled for
              the pipeline.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        return await self._patch(
            f"/v1-beta/pipelines/{pipeline_id}",
            body=await async_maybe_transform(
                {
                    "action_config": action_config,
                    "complex_tabular_transform_enabled": complex_tabular_transform_enabled,
                    "independent_document_processing_enabled": independent_document_processing_enabled,
                    "name": name,
                    "output_schema": output_schema,
                    "output_schema_name": output_schema_name,
                    "webhook_enabled": webhook_enabled,
                    "webhook_url": webhook_url,
                },
                pipeline_update_params.PipelineUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Pipeline,
        )

    async def list(
        self,
        *,
        ending_before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        starting_after: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PipelineListResponse:
        """
        Retrieves configurations for all existing pipelines.

        Args:
          ending_before: A cursor to use in pagination. `endingBefore` is a pipeline ID that defines your
              place in the list. For example, if you make a list request and receive 50
              objects, starting with `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call
              can include `endingBefore=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the previous
              page of the list.

          starting_after: A cursor to use in pagination. `startingAfter` is a pipeline ID that defines
              your place in the list. For example, if you make a list request and receive 50
              objects, ending with `pl_2c9AXIj48cUYJtCuv1gsQtHGDzK`, your subsequent call can
              include `startingAfter=pl_2c9AXIj48cUYJtCuv1gsQtHGDzK` to fetch the next page of
              the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1-beta/pipelines",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "ending_before": ending_before,
                        "limit": limit,
                        "starting_after": starting_after,
                    },
                    pipeline_list_params.PipelineListParams,
                ),
            ),
            cast_to=PipelineListResponse,
        )

    async def delete(
        self,
        pipeline_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes an existing pipeline and all related transformations.

        **IMPORTANT NOTE:** be sure you have exported any relevant transformations
        produced by the pipeline before deleting given they won't be accessible through
        our API after deleting the pipeline.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pipeline_id:
            raise ValueError(f"Expected a non-empty value for `pipeline_id` but received {pipeline_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1-beta/pipelines/{pipeline_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class PipelinesResourceWithRawResponse:
    def __init__(self, pipelines: PipelinesResource) -> None:
        self._pipelines = pipelines

        self.create = to_raw_response_wrapper(
            pipelines.create,
        )
        self.retrieve = to_raw_response_wrapper(
            pipelines.retrieve,
        )
        self.update = to_raw_response_wrapper(
            pipelines.update,
        )
        self.list = to_raw_response_wrapper(
            pipelines.list,
        )
        self.delete = to_raw_response_wrapper(
            pipelines.delete,
        )


class AsyncPipelinesResourceWithRawResponse:
    def __init__(self, pipelines: AsyncPipelinesResource) -> None:
        self._pipelines = pipelines

        self.create = async_to_raw_response_wrapper(
            pipelines.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            pipelines.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            pipelines.update,
        )
        self.list = async_to_raw_response_wrapper(
            pipelines.list,
        )
        self.delete = async_to_raw_response_wrapper(
            pipelines.delete,
        )


class PipelinesResourceWithStreamingResponse:
    def __init__(self, pipelines: PipelinesResource) -> None:
        self._pipelines = pipelines

        self.create = to_streamed_response_wrapper(
            pipelines.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            pipelines.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            pipelines.update,
        )
        self.list = to_streamed_response_wrapper(
            pipelines.list,
        )
        self.delete = to_streamed_response_wrapper(
            pipelines.delete,
        )


class AsyncPipelinesResourceWithStreamingResponse:
    def __init__(self, pipelines: AsyncPipelinesResource) -> None:
        self._pipelines = pipelines

        self.create = async_to_streamed_response_wrapper(
            pipelines.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            pipelines.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            pipelines.update,
        )
        self.list = async_to_streamed_response_wrapper(
            pipelines.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            pipelines.delete,
        )
