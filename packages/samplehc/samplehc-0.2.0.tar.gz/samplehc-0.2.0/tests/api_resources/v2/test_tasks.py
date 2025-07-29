# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Optional, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    TaskRetryResponse,
    TaskCompleteResponse,
    TaskUpdateScreenTimeResponse,
    TaskGetSuspendedPayloadResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_complete(self, client: SampleHealthcare) -> None:
        task = client.v2.tasks.complete(
            task_id="taskId",
        )
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_complete_with_all_params(self, client: SampleHealthcare) -> None:
        task = client.v2.tasks.complete(
            task_id="taskId",
            result={},
        )
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_complete(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.with_raw_response.complete(
            task_id="taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_complete(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.with_streaming_response.complete(
            task_id="taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskCompleteResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_complete(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.with_raw_response.complete(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_suspended_payload(self, client: SampleHealthcare) -> None:
        task = client.v2.tasks.get_suspended_payload(
            "taskId",
        )
        assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_suspended_payload(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.with_raw_response.get_suspended_payload(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_suspended_payload(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.with_streaming_response.get_suspended_payload(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_suspended_payload(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.with_raw_response.get_suspended_payload(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retry(self, client: SampleHealthcare) -> None:
        task = client.v2.tasks.retry(
            "taskId",
        )
        assert_matches_type(TaskRetryResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retry(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.with_raw_response.retry(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskRetryResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retry(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.with_streaming_response.retry(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskRetryResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retry(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.with_raw_response.retry(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_screen_time(self, client: SampleHealthcare) -> None:
        task = client.v2.tasks.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        )
        assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_screen_time(self, client: SampleHealthcare) -> None:
        response = client.v2.tasks.with_raw_response.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_screen_time(self, client: SampleHealthcare) -> None:
        with client.v2.tasks.with_streaming_response.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_screen_time(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.v2.tasks.with_raw_response.update_screen_time(
                task_id="",
                additional_screen_time=1,
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete(self, async_client: AsyncSampleHealthcare) -> None:
        task = await async_client.v2.tasks.complete(
            task_id="taskId",
        )
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_complete_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        task = await async_client.v2.tasks.complete(
            task_id="taskId",
            result={},
        )
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_complete(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.with_raw_response.complete(
            task_id="taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskCompleteResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_complete(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.with_streaming_response.complete(
            task_id="taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskCompleteResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_complete(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.with_raw_response.complete(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_suspended_payload(self, async_client: AsyncSampleHealthcare) -> None:
        task = await async_client.v2.tasks.get_suspended_payload(
            "taskId",
        )
        assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_suspended_payload(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.with_raw_response.get_suspended_payload(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_suspended_payload(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.with_streaming_response.get_suspended_payload(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskGetSuspendedPayloadResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_suspended_payload(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.with_raw_response.get_suspended_payload(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retry(self, async_client: AsyncSampleHealthcare) -> None:
        task = await async_client.v2.tasks.retry(
            "taskId",
        )
        assert_matches_type(TaskRetryResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retry(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.with_raw_response.retry(
            "taskId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskRetryResponse, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retry(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.with_streaming_response.retry(
            "taskId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskRetryResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retry(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.with_raw_response.retry(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_screen_time(self, async_client: AsyncSampleHealthcare) -> None:
        task = await async_client.v2.tasks.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        )
        assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_screen_time(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.tasks.with_raw_response.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_screen_time(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.tasks.with_streaming_response.update_screen_time(
            task_id="taskId",
            additional_screen_time=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Optional[TaskUpdateScreenTimeResponse], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_screen_time(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.v2.tasks.with_raw_response.update_screen_time(
                task_id="",
                additional_screen_time=1,
            )
