# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from quark import Quark, AsyncQuark
from quark.types import AgentRetrieveResponse, SuccessResponseMessage
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAgent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Quark) -> None:
        agent = client.agent.retrieve()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Quark) -> None:
        response = client.agent.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Quark) -> None:
        with client.agent.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_echo(self, client: Quark) -> None:
        agent = client.agent.echo()
        assert_matches_type(SuccessResponseMessage, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_echo(self, client: Quark) -> None:
        response = client.agent.with_raw_response.echo()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(SuccessResponseMessage, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_echo(self, client: Quark) -> None:
        with client.agent.with_streaming_response.echo() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(SuccessResponseMessage, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_one_step_rag_inference(self, client: Quark) -> None:
        agent = client.agent.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_one_step_rag_inference_with_all_params(self, client: Quark) -> None:
        agent = client.agent.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
            search_limit=0,
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_one_step_rag_inference(self, client: Quark) -> None:
        response = client.agent.with_raw_response.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_one_step_rag_inference(self, client: Quark) -> None:
        with client.agent.with_streaming_response.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(object, agent, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAgent:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncQuark) -> None:
        agent = await async_client.agent.retrieve()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncQuark) -> None:
        response = await async_client.agent.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncQuark) -> None:
        async with async_client.agent.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentRetrieveResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_echo(self, async_client: AsyncQuark) -> None:
        agent = await async_client.agent.echo()
        assert_matches_type(SuccessResponseMessage, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_echo(self, async_client: AsyncQuark) -> None:
        response = await async_client.agent.with_raw_response.echo()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(SuccessResponseMessage, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_echo(self, async_client: AsyncQuark) -> None:
        async with async_client.agent.with_streaming_response.echo() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(SuccessResponseMessage, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_one_step_rag_inference(self, async_client: AsyncQuark) -> None:
        agent = await async_client.agent.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_one_step_rag_inference_with_all_params(self, async_client: AsyncQuark) -> None:
        agent = await async_client.agent.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
            search_limit=0,
        )
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_one_step_rag_inference(self, async_client: AsyncQuark) -> None:
        response = await async_client.agent.with_raw_response.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(object, agent, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_one_step_rag_inference(self, async_client: AsyncQuark) -> None:
        async with async_client.agent.with_streaming_response.one_step_rag_inference(
            openai_api_key="openai_api_key",
            query="query",
            redact=True,
            table_name="table_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(object, agent, path=["response"])

        assert cast(Any, response.is_closed) is True
