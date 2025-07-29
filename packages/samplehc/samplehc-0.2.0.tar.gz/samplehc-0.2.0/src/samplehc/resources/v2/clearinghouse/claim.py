# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.clearinghouse import claim_submit_params
from ....types.v2.clearinghouse.claim_submit_response import ClaimSubmitResponse

__all__ = ["ClaimResource", "AsyncClaimResource"]


class ClaimResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClaimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return ClaimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClaimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return ClaimResourceWithStreamingResponse(self)

    def submit(
        self,
        *,
        input: claim_submit_params.Input,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClaimSubmitResponse:
        """Submits an electronic claim for processing.

        The submission is handled
        asynchronously, and this endpoint returns an identifier to track the status of
        the claim submission.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/clearinghouse/claim/submit",
            body=maybe_transform({"input": input}, claim_submit_params.ClaimSubmitParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClaimSubmitResponse,
        )


class AsyncClaimResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClaimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClaimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClaimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncClaimResourceWithStreamingResponse(self)

    async def submit(
        self,
        *,
        input: claim_submit_params.Input,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClaimSubmitResponse:
        """Submits an electronic claim for processing.

        The submission is handled
        asynchronously, and this endpoint returns an identifier to track the status of
        the claim submission.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/clearinghouse/claim/submit",
            body=await async_maybe_transform({"input": input}, claim_submit_params.ClaimSubmitParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClaimSubmitResponse,
        )


class ClaimResourceWithRawResponse:
    def __init__(self, claim: ClaimResource) -> None:
        self._claim = claim

        self.submit = to_raw_response_wrapper(
            claim.submit,
        )


class AsyncClaimResourceWithRawResponse:
    def __init__(self, claim: AsyncClaimResource) -> None:
        self._claim = claim

        self.submit = async_to_raw_response_wrapper(
            claim.submit,
        )


class ClaimResourceWithStreamingResponse:
    def __init__(self, claim: ClaimResource) -> None:
        self._claim = claim

        self.submit = to_streamed_response_wrapper(
            claim.submit,
        )


class AsyncClaimResourceWithStreamingResponse:
    def __init__(self, claim: AsyncClaimResource) -> None:
        self._claim = claim

        self.submit = async_to_streamed_response_wrapper(
            claim.submit,
        )
