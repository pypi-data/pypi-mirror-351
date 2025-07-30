# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.webhook_secret import WebhookSecret

__all__ = ["WebhookSecretResource", "AsyncWebhookSecretResource"]


class WebhookSecretResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WebhookSecretResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return WebhookSecretResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhookSecretResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return WebhookSecretResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookSecret:
        """Generates a new webhook secret to be used for webhook signatures.

        If a webhook
        secret already exists, this endpoint will overwrite the previous secret and
        generate a new one.
        """
        return self._post(
            "/v1-beta/webhook-secret",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookSecret,
        )

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookSecret:
        """Gets the current webhook secret for your account."""
        return self._get(
            "/v1-beta/webhook-secret",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookSecret,
        )


class AsyncWebhookSecretResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWebhookSecretResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhookSecretResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhookSecretResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bem-team/bem-sdk-python#with_streaming_response
        """
        return AsyncWebhookSecretResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookSecret:
        """Generates a new webhook secret to be used for webhook signatures.

        If a webhook
        secret already exists, this endpoint will overwrite the previous secret and
        generate a new one.
        """
        return await self._post(
            "/v1-beta/webhook-secret",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookSecret,
        )

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WebhookSecret:
        """Gets the current webhook secret for your account."""
        return await self._get(
            "/v1-beta/webhook-secret",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WebhookSecret,
        )


class WebhookSecretResourceWithRawResponse:
    def __init__(self, webhook_secret: WebhookSecretResource) -> None:
        self._webhook_secret = webhook_secret

        self.create = to_raw_response_wrapper(
            webhook_secret.create,
        )
        self.retrieve = to_raw_response_wrapper(
            webhook_secret.retrieve,
        )


class AsyncWebhookSecretResourceWithRawResponse:
    def __init__(self, webhook_secret: AsyncWebhookSecretResource) -> None:
        self._webhook_secret = webhook_secret

        self.create = async_to_raw_response_wrapper(
            webhook_secret.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            webhook_secret.retrieve,
        )


class WebhookSecretResourceWithStreamingResponse:
    def __init__(self, webhook_secret: WebhookSecretResource) -> None:
        self._webhook_secret = webhook_secret

        self.create = to_streamed_response_wrapper(
            webhook_secret.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            webhook_secret.retrieve,
        )


class AsyncWebhookSecretResourceWithStreamingResponse:
    def __init__(self, webhook_secret: AsyncWebhookSecretResource) -> None:
        self._webhook_secret = webhook_secret

        self.create = async_to_streamed_response_wrapper(
            webhook_secret.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            webhook_secret.retrieve,
        )
