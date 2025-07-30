# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.registry import lattice_register_params
from ...types.registry.quark_tag import QuarkTag
from ...types.success_response_message import SuccessResponseMessage
from ...types.registry.schema_info_param import SchemaInfoParam
from ...types.registry.lattice_flow_response import LatticeFlowResponse
from ...types.registry.lattice_registry_item import LatticeRegistryItem
from ...types.registry.described_input_field_param import DescribedInputFieldParam

__all__ = ["LatticeResource", "AsyncLatticeResource"]


class LatticeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LatticeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return LatticeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LatticeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return LatticeResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LatticeRegistryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            f"/registry/lattice/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LatticeRegistryItem,
        )

    def flow(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LatticeFlowResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._get(
            f"/registry/lattice/{id}/flow",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LatticeFlowResponse,
        )

    def register(
        self,
        *,
        author: str,
        edges: Iterable[lattice_register_params.Edge],
        hidden: bool,
        identifier: str,
        inputs: Iterable[DescribedInputFieldParam],
        lattice_type: Literal["DataIngest", "Inference", "Other"],
        name: str,
        nodes: Iterable[lattice_register_params.Node],
        tags: List[QuarkTag],
        version: str,
        description: str | NotGiven = NOT_GIVEN,
        output_schema: SchemaInfoParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        """
        Args:
          output_schema: API-Friendly representation of a [Schema]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return self._put(
            "/registry/lattice/register",
            body=maybe_transform(
                {
                    "author": author,
                    "edges": edges,
                    "hidden": hidden,
                    "identifier": identifier,
                    "inputs": inputs,
                    "lattice_type": lattice_type,
                    "name": name,
                    "nodes": nodes,
                    "tags": tags,
                    "version": version,
                    "description": description,
                    "output_schema": output_schema,
                },
                lattice_register_params.LatticeRegisterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )


class AsyncLatticeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLatticeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncLatticeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLatticeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncLatticeResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LatticeRegistryItem:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            f"/registry/lattice/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LatticeRegistryItem,
        )

    async def flow(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LatticeFlowResponse:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._get(
            f"/registry/lattice/{id}/flow",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LatticeFlowResponse,
        )

    async def register(
        self,
        *,
        author: str,
        edges: Iterable[lattice_register_params.Edge],
        hidden: bool,
        identifier: str,
        inputs: Iterable[DescribedInputFieldParam],
        lattice_type: Literal["DataIngest", "Inference", "Other"],
        name: str,
        nodes: Iterable[lattice_register_params.Node],
        tags: List[QuarkTag],
        version: str,
        description: str | NotGiven = NOT_GIVEN,
        output_schema: SchemaInfoParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SuccessResponseMessage:
        """
        Args:
          output_schema: API-Friendly representation of a [Schema]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json; charset=utf-8", **(extra_headers or {})}
        return await self._put(
            "/registry/lattice/register",
            body=await async_maybe_transform(
                {
                    "author": author,
                    "edges": edges,
                    "hidden": hidden,
                    "identifier": identifier,
                    "inputs": inputs,
                    "lattice_type": lattice_type,
                    "name": name,
                    "nodes": nodes,
                    "tags": tags,
                    "version": version,
                    "description": description,
                    "output_schema": output_schema,
                },
                lattice_register_params.LatticeRegisterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SuccessResponseMessage,
        )


class LatticeResourceWithRawResponse:
    def __init__(self, lattice: LatticeResource) -> None:
        self._lattice = lattice

        self.retrieve = to_raw_response_wrapper(
            lattice.retrieve,
        )
        self.flow = to_raw_response_wrapper(
            lattice.flow,
        )
        self.register = to_raw_response_wrapper(
            lattice.register,
        )


class AsyncLatticeResourceWithRawResponse:
    def __init__(self, lattice: AsyncLatticeResource) -> None:
        self._lattice = lattice

        self.retrieve = async_to_raw_response_wrapper(
            lattice.retrieve,
        )
        self.flow = async_to_raw_response_wrapper(
            lattice.flow,
        )
        self.register = async_to_raw_response_wrapper(
            lattice.register,
        )


class LatticeResourceWithStreamingResponse:
    def __init__(self, lattice: LatticeResource) -> None:
        self._lattice = lattice

        self.retrieve = to_streamed_response_wrapper(
            lattice.retrieve,
        )
        self.flow = to_streamed_response_wrapper(
            lattice.flow,
        )
        self.register = to_streamed_response_wrapper(
            lattice.register,
        )


class AsyncLatticeResourceWithStreamingResponse:
    def __init__(self, lattice: AsyncLatticeResource) -> None:
        self._lattice = lattice

        self.retrieve = async_to_streamed_response_wrapper(
            lattice.retrieve,
        )
        self.flow = async_to_streamed_response_wrapper(
            lattice.flow,
        )
        self.register = async_to_streamed_response_wrapper(
            lattice.register,
        )
