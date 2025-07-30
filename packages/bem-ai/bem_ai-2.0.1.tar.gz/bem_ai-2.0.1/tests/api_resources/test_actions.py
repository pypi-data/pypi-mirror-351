# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import (
    GetActionsResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestActions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_1(self, client: BemSDK) -> None:
        action = client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_1(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_1(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_2(self, client: BemSDK) -> None:
        action = client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_2(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_2(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_3(self, client: BemSDK) -> None:
        action = client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_3(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_3(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_4(self, client: BemSDK) -> None:
        action = client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_4(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_4(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_5(self, client: BemSDK) -> None:
        action = client.actions.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params_overload_5(self, client: BemSDK) -> None:
        action = client.actions.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
            actions=[
                {
                    "reference_id": "referenceID",
                    "template_variables": {},
                }
            ],
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_5(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_5(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BemSDK) -> None:
        action = client.actions.list()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: BemSDK) -> None:
        action = client.actions.list(
            action_ids=["string"],
            action_type="transform",
            action_type_config_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_correct_route(self, client: BemSDK) -> None:
        action = client.actions.correct_route()
        assert action is None

    @pytest.mark.skip()
    @parametrize
    def test_method_correct_route_with_all_params(self, client: BemSDK) -> None:
        action = client.actions.correct_route(
            route_actions=[
                {
                    "action_id": "actionID",
                    "corrected_choice": "correctedChoice",
                }
            ],
        )
        assert action is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_correct_route(self, client: BemSDK) -> None:
        response = client.actions.with_raw_response.correct_route()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert action is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_correct_route(self, client: BemSDK) -> None:
        with client.actions.with_streaming_response.correct_route() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True


class TestAsyncActions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.create(
            actions=[
                {
                    "reference_id": "referenceID",
                    "inputs": [
                        {
                            "input_content": "U3RhaW5sZXNzIHJvY2tz",
                            "input_type": "email",
                        }
                    ],
                    "join_type": "standard",
                }
            ],
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params_overload_5(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
            actions=[
                {
                    "reference_id": "referenceID",
                    "template_variables": {},
                }
            ],
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.create(
            action_type="transform",
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.list()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.list(
            action_ids=["string"],
            action_type="transform",
            action_type_config_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(GetActionsResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(GetActionsResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_correct_route(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.correct_route()
        assert action is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_correct_route_with_all_params(self, async_client: AsyncBemSDK) -> None:
        action = await async_client.actions.correct_route(
            route_actions=[
                {
                    "action_id": "actionID",
                    "corrected_choice": "correctedChoice",
                }
            ],
        )
        assert action is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_correct_route(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.actions.with_raw_response.correct_route()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert action is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_correct_route(self, async_client: AsyncBemSDK) -> None:
        async with async_client.actions.with_streaming_response.correct_route() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert action is None

        assert cast(Any, response.is_closed) is True
