# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import (
    Subscription,
    SubscriptionListResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSubscriptions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: BemSDK) -> None:
        subscription = client.subscriptions.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: BemSDK) -> None:
        subscription = client.subscriptions.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
            disabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: BemSDK) -> None:
        response = client.subscriptions.with_raw_response.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: BemSDK) -> None:
        with client.subscriptions.with_streaming_response.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: BemSDK) -> None:
        subscription = client.subscriptions.retrieve(
            "subscriptionID",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: BemSDK) -> None:
        response = client.subscriptions.with_raw_response.retrieve(
            "subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: BemSDK) -> None:
        with client.subscriptions.with_streaming_response.retrieve(
            "subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            client.subscriptions.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: BemSDK) -> None:
        subscription = client.subscriptions.update(
            subscription_id="subscriptionID",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: BemSDK) -> None:
        subscription = client.subscriptions.update(
            subscription_id="subscriptionID",
            action_type_config_id="actionTypeConfigID",
            disabled=True,
            name="name",
            type="transform",
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: BemSDK) -> None:
        response = client.subscriptions.with_raw_response.update(
            subscription_id="subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: BemSDK) -> None:
        with client.subscriptions.with_streaming_response.update(
            subscription_id="subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            client.subscriptions.with_raw_response.update(
                subscription_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BemSDK) -> None:
        subscription = client.subscriptions.list()
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: BemSDK) -> None:
        subscription = client.subscriptions.list(
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BemSDK) -> None:
        response = client.subscriptions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = response.parse()
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BemSDK) -> None:
        with client.subscriptions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = response.parse()
            assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: BemSDK) -> None:
        subscription = client.subscriptions.delete(
            "subscriptionID",
        )
        assert subscription is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: BemSDK) -> None:
        response = client.subscriptions.with_raw_response.delete(
            "subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = response.parse()
        assert subscription is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: BemSDK) -> None:
        with client.subscriptions.with_streaming_response.delete(
            "subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = response.parse()
            assert subscription is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            client.subscriptions.with_raw_response.delete(
                "",
            )


class TestAsyncSubscriptions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
            disabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.subscriptions.with_raw_response.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = await response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBemSDK) -> None:
        async with async_client.subscriptions.with_streaming_response.create(
            action_type_config_id="actionTypeConfigID",
            name="name",
            type="transform",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = await response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.retrieve(
            "subscriptionID",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.subscriptions.with_raw_response.retrieve(
            "subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = await response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        async with async_client.subscriptions.with_streaming_response.retrieve(
            "subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = await response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            await async_client.subscriptions.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.update(
            subscription_id="subscriptionID",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.update(
            subscription_id="subscriptionID",
            action_type_config_id="actionTypeConfigID",
            disabled=True,
            name="name",
            type="transform",
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.subscriptions.with_raw_response.update(
            subscription_id="subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = await response.parse()
        assert_matches_type(Subscription, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncBemSDK) -> None:
        async with async_client.subscriptions.with_streaming_response.update(
            subscription_id="subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = await response.parse()
            assert_matches_type(Subscription, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            await async_client.subscriptions.with_raw_response.update(
                subscription_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.list()
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.list(
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.subscriptions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = await response.parse()
        assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBemSDK) -> None:
        async with async_client.subscriptions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = await response.parse()
            assert_matches_type(SubscriptionListResponse, subscription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncBemSDK) -> None:
        subscription = await async_client.subscriptions.delete(
            "subscriptionID",
        )
        assert subscription is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.subscriptions.with_raw_response.delete(
            "subscriptionID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscription = await response.parse()
        assert subscription is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBemSDK) -> None:
        async with async_client.subscriptions.with_streaming_response.delete(
            "subscriptionID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscription = await response.parse()
            assert subscription is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subscription_id` but received ''"):
            await async_client.subscriptions.with_raw_response.delete(
                "",
            )
