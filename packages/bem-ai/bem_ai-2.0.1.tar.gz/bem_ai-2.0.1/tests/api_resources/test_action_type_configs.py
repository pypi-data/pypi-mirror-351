# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import (
    ActionTypeConfig,
    ActionTypeConfigListResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestActionTypeConfigs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_1(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_1(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_1(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_2(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_2(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_2(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_3(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_3(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_3(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_4(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_4(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_4(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_overload_5(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_overload_5(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_overload_5(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.retrieve(
            "actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.retrieve(
            "actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.retrieve(
            "actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_overload_1(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params_overload_1(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            complex_tabular_transform_enabled=True,
            independent_document_processing_enabled=False,
            name="name",
            next_action_type_config_id="nextActionTypeConfigID",
            output_schema={
                "value": {
                    "type": "object",
                    "required": ["tenders"],
                    "properties": {
                        "tenders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "loadReference",
                                    "origin",
                                    "destination",
                                    "weightTons",
                                    "loadType",
                                    "desiredDeliveryDate",
                                    "bidSubmissionDeadline",
                                    "submitter",
                                ],
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "The starting point of the shipment.",
                                    },
                                    "loadType": {
                                        "type": "string",
                                        "description": "The type of goods being shipped.",
                                    },
                                    "submitter": {
                                        "type": "object",
                                        "required": ["name", "position", "contactInfo"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Name of the person submitting the tender.",
                                            },
                                            "position": {
                                                "type": "string",
                                                "description": "Position of the submitter within their company.",
                                            },
                                            "contactInfo": {
                                                "type": "object",
                                                "required": ["email"],
                                                "properties": {
                                                    "email": {
                                                        "type": "string",
                                                        "format": "email",
                                                        "description": "Email address of the submitter.",
                                                    },
                                                    "phone": {
                                                        "type": "string",
                                                        "description": "Phone number of the submitter.",
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "weightTons": {
                                        "type": "number",
                                        "description": "The weight of the load in tons.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The endpoint of the shipment.",
                                    },
                                    "loadReference": {
                                        "type": "string",
                                        "description": "Unique identifier for the load tender.",
                                    },
                                    "desiredDeliveryDate": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The preferred date for the shipment to be delivered.",
                                    },
                                    "bidSubmissionDeadline": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The deadline for submitting bids.",
                                    },
                                },
                            },
                        }
                    },
                }
            },
            output_schema_name="Freight Load Schema",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_overload_1(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_overload_1(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_overload_1(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_overload_2(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params_overload_2(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            description="description",
            name="name",
            routes=[
                {
                    "name": "name",
                    "action_type_config_id": "actionTypeConfigID",
                    "description": "description",
                    "origin": {"email": {"patterns": ["string"]}},
                    "regex": {"patterns": ["string"]},
                }
            ],
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_overload_2(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_overload_2(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_overload_2(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_overload_3(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params_overload_3(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            name="name",
            print_page_split_config={"next_action_type_config_id": "nextActionTypeConfigID"},
            semantic_page_split_config={
                "item_classes": [
                    {
                        "name": "name",
                        "description": "description",
                        "next_action_type_config_id": "nextActionTypeConfigID",
                    }
                ]
            },
            split_type="splitType",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_overload_3(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_overload_3(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_overload_3(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_overload_4(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params_overload_4(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            join_type="standard",
            name="name",
            next_action_type_config_id="nextActionTypeConfigID",
            output_schema={
                "value": {
                    "type": "object",
                    "required": ["tenders"],
                    "properties": {
                        "tenders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "loadReference",
                                    "origin",
                                    "destination",
                                    "weightTons",
                                    "loadType",
                                    "desiredDeliveryDate",
                                    "bidSubmissionDeadline",
                                    "submitter",
                                ],
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "The starting point of the shipment.",
                                    },
                                    "loadType": {
                                        "type": "string",
                                        "description": "The type of goods being shipped.",
                                    },
                                    "submitter": {
                                        "type": "object",
                                        "required": ["name", "position", "contactInfo"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Name of the person submitting the tender.",
                                            },
                                            "position": {
                                                "type": "string",
                                                "description": "Position of the submitter within their company.",
                                            },
                                            "contactInfo": {
                                                "type": "object",
                                                "required": ["email"],
                                                "properties": {
                                                    "email": {
                                                        "type": "string",
                                                        "format": "email",
                                                        "description": "Email address of the submitter.",
                                                    },
                                                    "phone": {
                                                        "type": "string",
                                                        "description": "Phone number of the submitter.",
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "weightTons": {
                                        "type": "number",
                                        "description": "The weight of the load in tons.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The endpoint of the shipment.",
                                    },
                                    "loadReference": {
                                        "type": "string",
                                        "description": "Unique identifier for the load tender.",
                                    },
                                    "desiredDeliveryDate": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The preferred date for the shipment to be delivered.",
                                    },
                                    "bidSubmissionDeadline": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The deadline for submitting bids.",
                                    },
                                },
                            },
                        }
                    },
                }
            },
            output_schema_name="Freight Load Schema",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_overload_4(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_overload_4(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_overload_4(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_overload_5(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params_overload_5(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            body="body",
            from_email="dev@stainless.com",
            from_name="fromName",
            name="name",
            subject="subject",
            to_email="dev@stainless.com",
            to_name="toName",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_overload_5(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_overload_5(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_overload_5(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.list()
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.list(
            action_type="transform",
            action_type_config_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: BemSDK) -> None:
        action_type_config = client.action_type_configs.delete(
            "actionTypeConfigID",
        )
        assert action_type_config is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: BemSDK) -> None:
        response = client.action_type_configs.with_raw_response.delete(
            "actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = response.parse()
        assert action_type_config is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: BemSDK) -> None:
        with client.action_type_configs.with_streaming_response.delete(
            "actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = response.parse()
            assert action_type_config is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            client.action_type_configs.with_raw_response.delete(
                "",
            )


class TestAsyncActionTypeConfigs:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_3(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_4(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.create(
            body={"action_type": "transform"},
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.create(
            body={"action_type": "transform"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_overload_5(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.create(
            body={"action_type": "transform"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.retrieve(
            "actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.retrieve(
            "actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.retrieve(
            "actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_overload_1(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params_overload_1(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            complex_tabular_transform_enabled=True,
            independent_document_processing_enabled=False,
            name="name",
            next_action_type_config_id="nextActionTypeConfigID",
            output_schema={
                "value": {
                    "type": "object",
                    "required": ["tenders"],
                    "properties": {
                        "tenders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "loadReference",
                                    "origin",
                                    "destination",
                                    "weightTons",
                                    "loadType",
                                    "desiredDeliveryDate",
                                    "bidSubmissionDeadline",
                                    "submitter",
                                ],
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "The starting point of the shipment.",
                                    },
                                    "loadType": {
                                        "type": "string",
                                        "description": "The type of goods being shipped.",
                                    },
                                    "submitter": {
                                        "type": "object",
                                        "required": ["name", "position", "contactInfo"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Name of the person submitting the tender.",
                                            },
                                            "position": {
                                                "type": "string",
                                                "description": "Position of the submitter within their company.",
                                            },
                                            "contactInfo": {
                                                "type": "object",
                                                "required": ["email"],
                                                "properties": {
                                                    "email": {
                                                        "type": "string",
                                                        "format": "email",
                                                        "description": "Email address of the submitter.",
                                                    },
                                                    "phone": {
                                                        "type": "string",
                                                        "description": "Phone number of the submitter.",
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "weightTons": {
                                        "type": "number",
                                        "description": "The weight of the load in tons.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The endpoint of the shipment.",
                                    },
                                    "loadReference": {
                                        "type": "string",
                                        "description": "Unique identifier for the load tender.",
                                    },
                                    "desiredDeliveryDate": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The preferred date for the shipment to be delivered.",
                                    },
                                    "bidSubmissionDeadline": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The deadline for submitting bids.",
                                    },
                                },
                            },
                        }
                    },
                }
            },
            output_schema_name="Freight Load Schema",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_overload_1(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_overload_1(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_overload_1(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_overload_2(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params_overload_2(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            description="description",
            name="name",
            routes=[
                {
                    "name": "name",
                    "action_type_config_id": "actionTypeConfigID",
                    "description": "description",
                    "origin": {"email": {"patterns": ["string"]}},
                    "regex": {"patterns": ["string"]},
                }
            ],
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_overload_2(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_overload_2(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_overload_2(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_overload_3(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params_overload_3(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            name="name",
            print_page_split_config={"next_action_type_config_id": "nextActionTypeConfigID"},
            semantic_page_split_config={
                "item_classes": [
                    {
                        "name": "name",
                        "description": "description",
                        "next_action_type_config_id": "nextActionTypeConfigID",
                    }
                ]
            },
            split_type="splitType",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_overload_3(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_overload_3(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_overload_3(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_overload_4(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params_overload_4(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            join_type="standard",
            name="name",
            next_action_type_config_id="nextActionTypeConfigID",
            output_schema={
                "value": {
                    "type": "object",
                    "required": ["tenders"],
                    "properties": {
                        "tenders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "loadReference",
                                    "origin",
                                    "destination",
                                    "weightTons",
                                    "loadType",
                                    "desiredDeliveryDate",
                                    "bidSubmissionDeadline",
                                    "submitter",
                                ],
                                "properties": {
                                    "origin": {
                                        "type": "string",
                                        "description": "The starting point of the shipment.",
                                    },
                                    "loadType": {
                                        "type": "string",
                                        "description": "The type of goods being shipped.",
                                    },
                                    "submitter": {
                                        "type": "object",
                                        "required": ["name", "position", "contactInfo"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Name of the person submitting the tender.",
                                            },
                                            "position": {
                                                "type": "string",
                                                "description": "Position of the submitter within their company.",
                                            },
                                            "contactInfo": {
                                                "type": "object",
                                                "required": ["email"],
                                                "properties": {
                                                    "email": {
                                                        "type": "string",
                                                        "format": "email",
                                                        "description": "Email address of the submitter.",
                                                    },
                                                    "phone": {
                                                        "type": "string",
                                                        "description": "Phone number of the submitter.",
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    "weightTons": {
                                        "type": "number",
                                        "description": "The weight of the load in tons.",
                                    },
                                    "destination": {
                                        "type": "string",
                                        "description": "The endpoint of the shipment.",
                                    },
                                    "loadReference": {
                                        "type": "string",
                                        "description": "Unique identifier for the load tender.",
                                    },
                                    "desiredDeliveryDate": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The preferred date for the shipment to be delivered.",
                                    },
                                    "bidSubmissionDeadline": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "The deadline for submitting bids.",
                                    },
                                },
                            },
                        }
                    },
                }
            },
            output_schema_name="Freight Load Schema",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_overload_4(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_overload_4(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_overload_4(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_overload_5(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params_overload_5(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.update(
            action_type_config_id="actionTypeConfigID",
            body="body",
            from_email="dev@stainless.com",
            from_name="fromName",
            name="name",
            subject="subject",
            to_email="dev@stainless.com",
            to_name="toName",
        )
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_overload_5(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.update(
            action_type_config_id="actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_overload_5(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.update(
            action_type_config_id="actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfig, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_overload_5(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.update(
                action_type_config_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.list()
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.list(
            action_type="transform",
            action_type_config_ids=["string"],
            ending_before="endingBefore",
            limit=1,
            sort_order="asc",
            starting_after="startingAfter",
        )
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert_matches_type(ActionTypeConfigListResponse, action_type_config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncBemSDK) -> None:
        action_type_config = await async_client.action_type_configs.delete(
            "actionTypeConfigID",
        )
        assert action_type_config is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.action_type_configs.with_raw_response.delete(
            "actionTypeConfigID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action_type_config = await response.parse()
        assert action_type_config is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBemSDK) -> None:
        async with async_client.action_type_configs.with_streaming_response.delete(
            "actionTypeConfigID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action_type_config = await response.parse()
            assert action_type_config is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `action_type_config_id` but received ''"):
            await async_client.action_type_configs.with_raw_response.delete(
                "",
            )
