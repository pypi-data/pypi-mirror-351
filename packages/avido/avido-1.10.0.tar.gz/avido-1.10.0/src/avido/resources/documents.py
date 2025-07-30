# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal

import httpx

from ..types import DocumentStatus, document_list_params, document_create_params, document_update_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncOffsetPagination, AsyncOffsetPagination
from .._base_client import AsyncPaginator, make_request_options
from ..types.document import Document
from ..types.document_status import DocumentStatus
from ..types.document_list_response import DocumentListResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        assignee: str,
        content: str,
        status: DocumentStatus,
        title: str,
        metadata: Dict[str, object] | NotGiven = NOT_GIVEN,
        original_sentences: List[str] | NotGiven = NOT_GIVEN,
        parent_id: str | NotGiven = NOT_GIVEN,
        scrape_job_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Document:
        """
        Creates a new document with the provided information.

        Args:
          assignee: User ID of the person assigned to this document

          content: Content of the document

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the document

          metadata: Optional metadata associated with the document

          original_sentences: Array of original sentences from the source

          parent_id: Optional ID of the parent document

          scrape_job_id: Optional ID of the scrape job that generated this document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v0/documents",
            body=maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "status": status,
                    "title": title,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "parent_id": parent_id,
                    "scrape_job_id": scrape_job_id,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

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
    ) -> Document:
        """
        Retrieves detailed information about a specific document, including its
        parent-child relationships.

        Args:
          id: The unique identifier of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v0/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

    def update(
        self,
        id: str,
        *,
        assignee: str | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, object] | NotGiven = NOT_GIVEN,
        original_sentences: List[str] | NotGiven = NOT_GIVEN,
        parent_id: Optional[str] | NotGiven = NOT_GIVEN,
        status: DocumentStatus | NotGiven = NOT_GIVEN,
        title: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Document:
        """
        Updates an existing document with the provided information.

        Args:
          id: The unique identifier of the document

          assignee: User ID of the person assigned to this document

          content: Content of the document

          metadata: Optional metadata associated with the document

          original_sentences: Array of original sentences from the source

          parent_id: Optional ID of the parent document

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/v0/documents/{id}",
            body=maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "parent_id": parent_id,
                    "status": status,
                    "title": title,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

    def list(
        self,
        *,
        assignee: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        parent_id: str | NotGiven = NOT_GIVEN,
        scrape_job_id: str | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncOffsetPagination[DocumentListResponse]:
        """
        Retrieves a paginated list of documents with optional filtering by status,
        assignee, parent, and other criteria.

        Args:
          assignee: Filter by assignee user ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          parent_id: Filter by parent document ID

          scrape_job_id: Filter by scrape job ID

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents",
            page=SyncOffsetPagination[DocumentListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "assignee": assignee,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "parent_id": parent_id,
                        "scrape_job_id": scrape_job_id,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=DocumentListResponse,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Avido-AI/avido-py#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Avido-AI/avido-py#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        assignee: str,
        content: str,
        status: DocumentStatus,
        title: str,
        metadata: Dict[str, object] | NotGiven = NOT_GIVEN,
        original_sentences: List[str] | NotGiven = NOT_GIVEN,
        parent_id: str | NotGiven = NOT_GIVEN,
        scrape_job_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Document:
        """
        Creates a new document with the provided information.

        Args:
          assignee: User ID of the person assigned to this document

          content: Content of the document

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the document

          metadata: Optional metadata associated with the document

          original_sentences: Array of original sentences from the source

          parent_id: Optional ID of the parent document

          scrape_job_id: Optional ID of the scrape job that generated this document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v0/documents",
            body=await async_maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "status": status,
                    "title": title,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "parent_id": parent_id,
                    "scrape_job_id": scrape_job_id,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

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
    ) -> Document:
        """
        Retrieves detailed information about a specific document, including its
        parent-child relationships.

        Args:
          id: The unique identifier of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v0/documents/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

    async def update(
        self,
        id: str,
        *,
        assignee: str | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, object] | NotGiven = NOT_GIVEN,
        original_sentences: List[str] | NotGiven = NOT_GIVEN,
        parent_id: Optional[str] | NotGiven = NOT_GIVEN,
        status: DocumentStatus | NotGiven = NOT_GIVEN,
        title: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Document:
        """
        Updates an existing document with the provided information.

        Args:
          id: The unique identifier of the document

          assignee: User ID of the person assigned to this document

          content: Content of the document

          metadata: Optional metadata associated with the document

          original_sentences: Array of original sentences from the source

          parent_id: Optional ID of the parent document

          status: Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED.

          title: Title of the document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/v0/documents/{id}",
            body=await async_maybe_transform(
                {
                    "assignee": assignee,
                    "content": content,
                    "metadata": metadata,
                    "original_sentences": original_sentences,
                    "parent_id": parent_id,
                    "status": status,
                    "title": title,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Document,
        )

    def list(
        self,
        *,
        assignee: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_dir: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        parent_id: str | NotGiven = NOT_GIVEN,
        scrape_job_id: str | NotGiven = NOT_GIVEN,
        skip: int | NotGiven = NOT_GIVEN,
        status: Literal["DRAFT", "REVIEW", "APPROVED", "ARCHIVED"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[DocumentListResponse, AsyncOffsetPagination[DocumentListResponse]]:
        """
        Retrieves a paginated list of documents with optional filtering by status,
        assignee, parent, and other criteria.

        Args:
          assignee: Filter by assignee user ID

          limit: Number of items per page

          order_by: Field to order by

          order_dir: Order direction

          parent_id: Filter by parent document ID

          scrape_job_id: Filter by scrape job ID

          skip: Number of items to skip

          status: Filter by document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/v0/documents",
            page=AsyncOffsetPagination[DocumentListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "assignee": assignee,
                        "limit": limit,
                        "order_by": order_by,
                        "order_dir": order_dir,
                        "parent_id": parent_id,
                        "scrape_job_id": scrape_job_id,
                        "skip": skip,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=DocumentListResponse,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = to_raw_response_wrapper(
            documents.retrieve,
        )
        self.update = to_raw_response_wrapper(
            documents.update,
        )
        self.list = to_raw_response_wrapper(
            documents.list,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_raw_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            documents.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            documents.update,
        )
        self.list = async_to_raw_response_wrapper(
            documents.list,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.create = to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            documents.update,
        )
        self.list = to_streamed_response_wrapper(
            documents.list,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.create = async_to_streamed_response_wrapper(
            documents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            documents.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            documents.update,
        )
        self.list = async_to_streamed_response_wrapper(
            documents.list,
        )
