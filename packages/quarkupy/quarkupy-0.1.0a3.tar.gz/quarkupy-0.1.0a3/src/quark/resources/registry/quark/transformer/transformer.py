# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from .docling_chunker import (
    DoclingChunkerResource,
    AsyncDoclingChunkerResource,
    DoclingChunkerResourceWithRawResponse,
    AsyncDoclingChunkerResourceWithRawResponse,
    DoclingChunkerResourceWithStreamingResponse,
    AsyncDoclingChunkerResourceWithStreamingResponse,
)
from .handlebars_base import (
    HandlebarsBaseResource,
    AsyncHandlebarsBaseResource,
    HandlebarsBaseResourceWithRawResponse,
    AsyncHandlebarsBaseResourceWithRawResponse,
    HandlebarsBaseResourceWithStreamingResponse,
    AsyncHandlebarsBaseResourceWithStreamingResponse,
)

__all__ = ["TransformerResource", "AsyncTransformerResource"]


class TransformerResource(SyncAPIResource):
    @cached_property
    def docling_chunker(self) -> DoclingChunkerResource:
        return DoclingChunkerResource(self._client)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResource:
        return HandlebarsBaseResource(self._client)

    @cached_property
    def with_raw_response(self) -> TransformerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return TransformerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TransformerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return TransformerResourceWithStreamingResponse(self)


class AsyncTransformerResource(AsyncAPIResource):
    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResource:
        return AsyncDoclingChunkerResource(self._client)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResource:
        return AsyncHandlebarsBaseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTransformerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/quarklabsai/quarkupy#accessing-raw-response-data-eg-headers
        """
        return AsyncTransformerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTransformerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/quarklabsai/quarkupy#with_streaming_response
        """
        return AsyncTransformerResourceWithStreamingResponse(self)


class TransformerResourceWithRawResponse:
    def __init__(self, transformer: TransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> DoclingChunkerResourceWithRawResponse:
        return DoclingChunkerResourceWithRawResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResourceWithRawResponse:
        return HandlebarsBaseResourceWithRawResponse(self._transformer.handlebars_base)


class AsyncTransformerResourceWithRawResponse:
    def __init__(self, transformer: AsyncTransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResourceWithRawResponse:
        return AsyncDoclingChunkerResourceWithRawResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResourceWithRawResponse:
        return AsyncHandlebarsBaseResourceWithRawResponse(self._transformer.handlebars_base)


class TransformerResourceWithStreamingResponse:
    def __init__(self, transformer: TransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> DoclingChunkerResourceWithStreamingResponse:
        return DoclingChunkerResourceWithStreamingResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> HandlebarsBaseResourceWithStreamingResponse:
        return HandlebarsBaseResourceWithStreamingResponse(self._transformer.handlebars_base)


class AsyncTransformerResourceWithStreamingResponse:
    def __init__(self, transformer: AsyncTransformerResource) -> None:
        self._transformer = transformer

    @cached_property
    def docling_chunker(self) -> AsyncDoclingChunkerResourceWithStreamingResponse:
        return AsyncDoclingChunkerResourceWithStreamingResponse(self._transformer.docling_chunker)

    @cached_property
    def handlebars_base(self) -> AsyncHandlebarsBaseResourceWithStreamingResponse:
        return AsyncHandlebarsBaseResourceWithStreamingResponse(self._transformer.handlebars_base)
