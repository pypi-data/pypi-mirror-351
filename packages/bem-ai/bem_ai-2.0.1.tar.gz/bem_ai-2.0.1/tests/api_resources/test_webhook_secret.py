# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import WebhookSecret
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhookSecret:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: BemSDK) -> None:
        webhook_secret = client.webhook_secret.create()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: BemSDK) -> None:
        response = client.webhook_secret.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_secret = response.parse()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: BemSDK) -> None:
        with client.webhook_secret.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_secret = response.parse()
            assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: BemSDK) -> None:
        webhook_secret = client.webhook_secret.retrieve()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: BemSDK) -> None:
        response = client.webhook_secret.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_secret = response.parse()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: BemSDK) -> None:
        with client.webhook_secret.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_secret = response.parse()
            assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWebhookSecret:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncBemSDK) -> None:
        webhook_secret = await async_client.webhook_secret.create()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.webhook_secret.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_secret = await response.parse()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBemSDK) -> None:
        async with async_client.webhook_secret.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_secret = await response.parse()
            assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBemSDK) -> None:
        webhook_secret = await async_client.webhook_secret.retrieve()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.webhook_secret.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook_secret = await response.parse()
        assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        async with async_client.webhook_secret.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook_secret = await response.parse()
            assert_matches_type(WebhookSecret, webhook_secret, path=["response"])

        assert cast(Any, response.is_closed) is True
