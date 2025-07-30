# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quark import Quark, AsyncQuark
from quark.types import SuccessResponseMessage
from tests.utils import assert_matches_type
from quark.types.registry import LatticeFlowResponse, LatticeRegistryItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLattice:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        lattice = client.registry.lattice.retrieve(
            "id",
        )
        assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.registry.lattice.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = response.parse()
        assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.registry.lattice.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = response.parse()
            assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.registry.lattice.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_flow(self, client: Quark) -> None:
        lattice = client.registry.lattice.flow(
            "id",
        )
        assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_flow(self, client: Quark) -> None:
        response = client.registry.lattice.with_raw_response.flow(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = response.parse()
        assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_flow(self, client: Quark) -> None:
        with client.registry.lattice.with_streaming_response.flow(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = response.parse()
            assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_flow(self, client: Quark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.registry.lattice.with_raw_response.flow(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_register(self, client: Quark) -> None:
        lattice = client.registry.lattice.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        )
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_register_with_all_params(self, client: Quark) -> None:
        lattice = client.registry.lattice.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                    "default_value": {},
                    "description": "description",
                    "ipc_schema": {
                        "extra_fields_allowed": True,
                        "fields": [
                            {
                                "data_type": "data_type",
                                "name": "name",
                                "description": "description",
                            }
                        ],
                    },
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                    "description": "description",
                }
            ],
            tags=["AI"],
            version="version",
            description="description",
            output_schema={
                "extra_fields_allowed": True,
                "fields": [
                    {
                        "data_type": "data_type",
                        "name": "name",
                        "description": "description",
                    }
                ],
            },
        )
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_register(self, client: Quark) -> None:
        response = client.registry.lattice.with_raw_response.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = response.parse()
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_register(self, client: Quark) -> None:
        with client.registry.lattice.with_streaming_response.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = response.parse()
            assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLattice:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        lattice = await async_client.registry.lattice.retrieve(
            "id",
        )
        assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.registry.lattice.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = await response.parse()
        assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.registry.lattice.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = await response.parse()
            assert_matches_type(LatticeRegistryItem, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.registry.lattice.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_flow(self, async_client: AsyncQuark) -> None:
        lattice = await async_client.registry.lattice.flow(
            "id",
        )
        assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_flow(self, async_client: AsyncQuark) -> None:
        response = await async_client.registry.lattice.with_raw_response.flow(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = await response.parse()
        assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_flow(self, async_client: AsyncQuark) -> None:
        async with async_client.registry.lattice.with_streaming_response.flow(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = await response.parse()
            assert_matches_type(LatticeFlowResponse, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_flow(self, async_client: AsyncQuark) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.registry.lattice.with_raw_response.flow(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_register(self, async_client: AsyncQuark) -> None:
        lattice = await async_client.registry.lattice.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        )
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_register_with_all_params(self, async_client: AsyncQuark) -> None:
        lattice = await async_client.registry.lattice.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                    "default_value": {},
                    "description": "description",
                    "ipc_schema": {
                        "extra_fields_allowed": True,
                        "fields": [
                            {
                                "data_type": "data_type",
                                "name": "name",
                                "description": "description",
                            }
                        ],
                    },
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                    "description": "description",
                }
            ],
            tags=["AI"],
            version="version",
            description="description",
            output_schema={
                "extra_fields_allowed": True,
                "fields": [
                    {
                        "data_type": "data_type",
                        "name": "name",
                        "description": "description",
                    }
                ],
            },
        )
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_register(self, async_client: AsyncQuark) -> None:
        response = await async_client.registry.lattice.with_raw_response.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        lattice = await response.parse()
        assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_register(self, async_client: AsyncQuark) -> None:
        async with async_client.registry.lattice.with_streaming_response.register(
            author="author",
            edges=[
                {
                    "source_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "target_node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
            hidden=True,
            identifier="identifier",
            inputs=[
                {
                    "advanced": True,
                    "field_name": "field_name",
                    "field_type": "field_type",
                    "friendly_name": "friendly_name",
                    "required": True,
                    "sensitive": True,
                }
            ],
            lattice_type="DataIngest",
            name="name",
            nodes=[
                {
                    "constants": {"foo": "bar"},
                    "lattice_to_quark_input_map": {"foo": "string"},
                    "name": "name",
                    "node_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "quark_reg_id": "quark_reg_id",
                }
            ],
            tags=["AI"],
            version="version",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            lattice = await response.parse()
            assert_matches_type(SuccessResponseMessage, lattice, path=["response"])

        assert cast(Any, response.is_closed) is True
