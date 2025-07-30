# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bem import BemSDK, AsyncBemSDK
from bem.types import (
    Pipeline,
    PipelineListResponse,
    PipelineRetrieveResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPipelines:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: BemSDK) -> None:
        pipeline = client.pipelines.create(
            name="Freight Load Pipeline",
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
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: BemSDK) -> None:
        pipeline = client.pipelines.create(
            name="Freight Load Pipeline",
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
            action_config={
                "action_type_config_id": "actionTypeConfigID",
                "name": "name",
                "action_type": "transform",
                "complex_tabular_transform_enabled": True,
                "email_address": "eml_2c9AXFXHwiaL4vPXDTOS171OJ8T@pipeline.bem.ai",
                "independent_document_processing_enabled": False,
                "output_schema": {
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
                "output_schema_name": "Freight Load Schema",
                "next_action_type_config_id": "nextActionTypeConfigID",
            },
            complex_tabular_transform_enabled=False,
            independent_document_processing_enabled=False,
            output_schema_name="Freight Load Schema",
            webhook_enabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: BemSDK) -> None:
        response = client.pipelines.with_raw_response.create(
            name="Freight Load Pipeline",
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
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = response.parse()
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: BemSDK) -> None:
        with client.pipelines.with_streaming_response.create(
            name="Freight Load Pipeline",
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
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = response.parse()
            assert_matches_type(Pipeline, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: BemSDK) -> None:
        pipeline = client.pipelines.retrieve(
            "pipelineID",
        )
        assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: BemSDK) -> None:
        response = client.pipelines.with_raw_response.retrieve(
            "pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = response.parse()
        assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: BemSDK) -> None:
        with client.pipelines.with_streaming_response.retrieve(
            "pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = response.parse()
            assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            client.pipelines.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: BemSDK) -> None:
        pipeline = client.pipelines.update(
            pipeline_id="pipelineID",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: BemSDK) -> None:
        pipeline = client.pipelines.update(
            pipeline_id="pipelineID",
            action_config={
                "action_type_config_id": "actionTypeConfigID",
                "name": "name",
                "action_type": "transform",
                "complex_tabular_transform_enabled": True,
                "email_address": "eml_2c9AXFXHwiaL4vPXDTOS171OJ8T@pipeline.bem.ai",
                "independent_document_processing_enabled": False,
                "output_schema": {
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
                "output_schema_name": "Freight Load Schema",
                "next_action_type_config_id": "nextActionTypeConfigID",
            },
            complex_tabular_transform_enabled=False,
            independent_document_processing_enabled=False,
            name="Freight invoices pipeline",
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
            output_schema_name="Freight invoices schema",
            webhook_enabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: BemSDK) -> None:
        response = client.pipelines.with_raw_response.update(
            pipeline_id="pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = response.parse()
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: BemSDK) -> None:
        with client.pipelines.with_streaming_response.update(
            pipeline_id="pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = response.parse()
            assert_matches_type(Pipeline, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            client.pipelines.with_raw_response.update(
                pipeline_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: BemSDK) -> None:
        pipeline = client.pipelines.list()
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: BemSDK) -> None:
        pipeline = client.pipelines.list(
            ending_before="endingBefore",
            limit=1,
            starting_after="startingAfter",
        )
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: BemSDK) -> None:
        response = client.pipelines.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = response.parse()
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: BemSDK) -> None:
        with client.pipelines.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = response.parse()
            assert_matches_type(PipelineListResponse, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: BemSDK) -> None:
        pipeline = client.pipelines.delete(
            "pipelineID",
        )
        assert pipeline is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: BemSDK) -> None:
        response = client.pipelines.with_raw_response.delete(
            "pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = response.parse()
        assert pipeline is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: BemSDK) -> None:
        with client.pipelines.with_streaming_response.delete(
            "pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = response.parse()
            assert pipeline is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: BemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            client.pipelines.with_raw_response.delete(
                "",
            )


class TestAsyncPipelines:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.create(
            name="Freight Load Pipeline",
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
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.create(
            name="Freight Load Pipeline",
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
            action_config={
                "action_type_config_id": "actionTypeConfigID",
                "name": "name",
                "action_type": "transform",
                "complex_tabular_transform_enabled": True,
                "email_address": "eml_2c9AXFXHwiaL4vPXDTOS171OJ8T@pipeline.bem.ai",
                "independent_document_processing_enabled": False,
                "output_schema": {
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
                "output_schema_name": "Freight Load Schema",
                "next_action_type_config_id": "nextActionTypeConfigID",
            },
            complex_tabular_transform_enabled=False,
            independent_document_processing_enabled=False,
            output_schema_name="Freight Load Schema",
            webhook_enabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.pipelines.with_raw_response.create(
            name="Freight Load Pipeline",
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
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = await response.parse()
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncBemSDK) -> None:
        async with async_client.pipelines.with_streaming_response.create(
            name="Freight Load Pipeline",
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
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = await response.parse()
            assert_matches_type(Pipeline, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.retrieve(
            "pipelineID",
        )
        assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.pipelines.with_raw_response.retrieve(
            "pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = await response.parse()
        assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncBemSDK) -> None:
        async with async_client.pipelines.with_streaming_response.retrieve(
            "pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = await response.parse()
            assert_matches_type(PipelineRetrieveResponse, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            await async_client.pipelines.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.update(
            pipeline_id="pipelineID",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.update(
            pipeline_id="pipelineID",
            action_config={
                "action_type_config_id": "actionTypeConfigID",
                "name": "name",
                "action_type": "transform",
                "complex_tabular_transform_enabled": True,
                "email_address": "eml_2c9AXFXHwiaL4vPXDTOS171OJ8T@pipeline.bem.ai",
                "independent_document_processing_enabled": False,
                "output_schema": {
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
                "output_schema_name": "Freight Load Schema",
                "next_action_type_config_id": "nextActionTypeConfigID",
            },
            complex_tabular_transform_enabled=False,
            independent_document_processing_enabled=False,
            name="Freight invoices pipeline",
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
            output_schema_name="Freight invoices schema",
            webhook_enabled=True,
            webhook_url="https://bem-example.ai/test/url",
        )
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.pipelines.with_raw_response.update(
            pipeline_id="pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = await response.parse()
        assert_matches_type(Pipeline, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncBemSDK) -> None:
        async with async_client.pipelines.with_streaming_response.update(
            pipeline_id="pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = await response.parse()
            assert_matches_type(Pipeline, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            await async_client.pipelines.with_raw_response.update(
                pipeline_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.list()
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.list(
            ending_before="endingBefore",
            limit=1,
            starting_after="startingAfter",
        )
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.pipelines.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = await response.parse()
        assert_matches_type(PipelineListResponse, pipeline, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBemSDK) -> None:
        async with async_client.pipelines.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = await response.parse()
            assert_matches_type(PipelineListResponse, pipeline, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncBemSDK) -> None:
        pipeline = await async_client.pipelines.delete(
            "pipelineID",
        )
        assert pipeline is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBemSDK) -> None:
        response = await async_client.pipelines.with_raw_response.delete(
            "pipelineID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        pipeline = await response.parse()
        assert pipeline is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBemSDK) -> None:
        async with async_client.pipelines.with_streaming_response.delete(
            "pipelineID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            pipeline = await response.parse()
            assert pipeline is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBemSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pipeline_id` but received ''"):
            await async_client.pipelines.with_raw_response.delete(
                "",
            )
