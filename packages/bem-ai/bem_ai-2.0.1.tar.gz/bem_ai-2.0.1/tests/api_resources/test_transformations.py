# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import (
    TransformationListResponse,
    TransformationCreateResponse,
    TransformationDeleteResponse,
    UpdateTransformationResponse,
    TransformationListErrorsResponse,
)
from bem._utils import parse_datetime
from tests.utils import assert_matches_type

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTransformations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: BemSDK) -> None:
        transformation = client.transformations.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        )
        assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: BemSDK) -> None:
        response = client.transformations.with_raw_response.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: BemSDK) -> None:
        with client.transformations.with_streaming_response.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = response.parse()
            assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: BemSDK) -> None:
        transformation = client.transformations.update()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: BemSDK) -> None:
        transformation = client.transformations.update(
            transformations=[
                {
                    "corrected_json": {},
                    "order_matching": True,
                    "transformation_id": "transformationID",
                }
            ],
        )
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: BemSDK) -> None:
        response = client.transformations.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: BemSDK) -> None:
        with client.transformations.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = response.parse()
            assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BemSDK) -> None:
        transformation = client.transformations.list()
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: BemSDK) -> None:
        transformation = client.transformations.list(
            ending_before="endingBefore",
            item_offset=0,
            limit=1,
            pipeline_id="pipelineID",
            published=True,
            published_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            published_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            reference_ids=["string"],
            sort_order="asc",
            starting_after="startingAfter",
            transformation_ids=["string"],
        )
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BemSDK) -> None:
        response = client.transformations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BemSDK) -> None:
        with client.transformations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = response.parse()
            assert_matches_type(TransformationListResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: BemSDK) -> None:
        transformation = client.transformations.delete()
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_with_all_params(self, client: BemSDK) -> None:
        transformation = client.transformations.delete(
            pipeline_id="pipelineID",
            reference_ids=["string"],
            transformation_ids=["string"],
        )
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: BemSDK) -> None:
        response = client.transformations.with_raw_response.delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: BemSDK) -> None:
        with client.transformations.with_streaming_response.delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = response.parse()
            assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_deprecated_update(self, client: BemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            transformation = client.transformations.deprecated_update()

        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_deprecated_update_with_all_params(self, client: BemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            transformation = client.transformations.deprecated_update(
                transformations=[
                    {
                        "corrected_json": {},
                        "order_matching": True,
                        "transformation_id": "transformationID",
                    }
                ],
            )

        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_deprecated_update(self, client: BemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.transformations.with_raw_response.deprecated_update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_deprecated_update(self, client: BemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            with client.transformations.with_streaming_response.deprecated_update() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                transformation = response.parse()
                assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_errors(self, client: BemSDK) -> None:
        transformation = client.transformations.list_errors(
            reference_ids=["string"],
        )
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_errors_with_all_params(self, client: BemSDK) -> None:
        transformation = client.transformations.list_errors(
            reference_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            pipeline_id="pipelineID",
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_errors(self, client: BemSDK) -> None:
        response = client.transformations.with_raw_response.list_errors(
            reference_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = response.parse()
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_errors(self, client: BemSDK) -> None:
        with client.transformations.with_streaming_response.list_errors(
            reference_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = response.parse()
            assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTransformations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        )
        assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.transformations.with_raw_response.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBemSDK) -> None:
        async with async_client.transformations.with_streaming_response.create(
            pipeline_id="pl_2c9AXIj48cUYJtCuv1gsQtHGDzK",
            transformations=[
                {
                    "input_content": "U3RhaW5sZXNzIHJvY2tz",
                    "input_type": "email",
                    "reference_id": "referenceID",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = await response.parse()
            assert_matches_type(TransformationCreateResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.update()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.update(
            transformations=[
                {
                    "corrected_json": {},
                    "order_matching": True,
                    "transformation_id": "transformationID",
                }
            ],
        )
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.transformations.with_raw_response.update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncBemSDK) -> None:
        async with async_client.transformations.with_streaming_response.update() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = await response.parse()
            assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.list()
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.list(
            ending_before="endingBefore",
            item_offset=0,
            limit=1,
            pipeline_id="pipelineID",
            published=True,
            published_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            published_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            reference_ids=["string"],
            sort_order="asc",
            starting_after="startingAfter",
            transformation_ids=["string"],
        )
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.transformations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(TransformationListResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBemSDK) -> None:
        async with async_client.transformations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = await response.parse()
            assert_matches_type(TransformationListResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.delete()
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.delete(
            pipeline_id="pipelineID",
            reference_ids=["string"],
            transformation_ids=["string"],
        )
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.transformations.with_raw_response.delete()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBemSDK) -> None:
        async with async_client.transformations.with_streaming_response.delete() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = await response.parse()
            assert_matches_type(TransformationDeleteResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_deprecated_update(self, async_client: AsyncBemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            transformation = await async_client.transformations.deprecated_update()

        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_deprecated_update_with_all_params(self, async_client: AsyncBemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            transformation = await async_client.transformations.deprecated_update(
                transformations=[
                    {
                        "corrected_json": {},
                        "order_matching": True,
                        "transformation_id": "transformationID",
                    }
                ],
            )

        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_deprecated_update(self, async_client: AsyncBemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.transformations.with_raw_response.deprecated_update()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_deprecated_update(self, async_client: AsyncBemSDK) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.transformations.with_streaming_response.deprecated_update() as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                transformation = await response.parse()
                assert_matches_type(UpdateTransformationResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_errors(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.list_errors(
            reference_ids=["string"],
        )
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_errors_with_all_params(self, async_client: AsyncBemSDK) -> None:
        transformation = await async_client.transformations.list_errors(
            reference_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            pipeline_id="pipelineID",
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_errors(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.transformations.with_raw_response.list_errors(
            reference_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transformation = await response.parse()
        assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_errors(self, async_client: AsyncBemSDK) -> None:
        async with async_client.transformations.with_streaming_response.list_errors(
            reference_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transformation = await response.parse()
            assert_matches_type(TransformationListErrorsResponse, transformation, path=["response"])

        assert cast(Any, response.is_closed) is True
