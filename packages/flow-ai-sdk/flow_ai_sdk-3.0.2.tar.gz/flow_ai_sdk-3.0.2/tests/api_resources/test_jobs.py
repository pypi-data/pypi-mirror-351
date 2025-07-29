# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from flow_ai_sdk import FlowAISDK, AsyncFlowAISDK
from tests.utils import assert_matches_type
from flow_ai_sdk.types import (
    Job,
    JobCancelResponse,
    JobBatchGeneration,
    JobGenerateDatasetResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: FlowAISDK) -> None:
        job = client.jobs.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Job, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(Job, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(Job, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: FlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.jobs.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_cancel(self, client: FlowAISDK) -> None:
        job = client.jobs.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JobCancelResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_cancel(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(JobCancelResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_cancel(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(JobCancelResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_cancel(self, client: FlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.jobs.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_batch(self, client: FlowAISDK) -> None:
        job = client.jobs.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_generate_batch(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_generate_batch(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(JobBatchGeneration, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_generate_batch(self, client: FlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.jobs.with_raw_response.generate_batch(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_dataset(self, client: FlowAISDK) -> None:
        job = client.jobs.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_generate_dataset_with_all_params(self, client: FlowAISDK) -> None:
        job = client.jobs.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            description="description",
        )
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_generate_dataset(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_generate_dataset(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_generate_dataset(self, client: FlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.jobs.with_raw_response.generate_dataset(
                job_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list_batches(self, client: FlowAISDK) -> None:
        job = client.jobs.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_batches_with_all_params(self, client: FlowAISDK) -> None:
        job = client.jobs.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_batches(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_batches(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(object, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list_batches(self, client: FlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.jobs.with_raw_response.list_batches(
                job_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_trigger_pipeline(self, client: FlowAISDK) -> None:
        job = client.jobs.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        )
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_trigger_pipeline(self, client: FlowAISDK) -> None:
        response = client.jobs.with_raw_response.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_trigger_pipeline(self, client: FlowAISDK) -> None:
        with client.jobs.with_streaming_response.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(JobBatchGeneration, job, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncJobs:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Job, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(Job, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(Job, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncFlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.jobs.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_cancel(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JobCancelResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(JobCancelResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.cancel(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(JobCancelResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncFlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.jobs.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_batch(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_generate_batch(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_generate_batch(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.generate_batch(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(JobBatchGeneration, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_generate_batch(self, async_client: AsyncFlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.jobs.with_raw_response.generate_batch(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_dataset(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_generate_dataset_with_all_params(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
            description="description",
        )
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_generate_dataset(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_generate_dataset(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.generate_dataset(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(JobGenerateDatasetResponse, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_generate_dataset(self, async_client: AsyncFlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.jobs.with_raw_response.generate_dataset(
                job_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_batches(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_batches_with_all_params(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            limit=1,
            offset=0,
        )
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_batches(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(object, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_batches(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.list_batches(
            job_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(object, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list_batches(self, async_client: AsyncFlowAISDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.jobs.with_raw_response.list_batches(
                job_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_trigger_pipeline(self, async_client: AsyncFlowAISDK) -> None:
        job = await async_client.jobs.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        )
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_trigger_pipeline(self, async_client: AsyncFlowAISDK) -> None:
        response = await async_client.jobs.with_raw_response.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = await response.parse()
        assert_matches_type(JobBatchGeneration, job, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_trigger_pipeline(self, async_client: AsyncFlowAISDK) -> None:
        async with async_client.jobs.with_streaming_response.trigger_pipeline(
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            body=[
                {
                    "id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "s3_path": "s3_path",
                    "source_type": "source_type",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(JobBatchGeneration, job, path=["response"])

        assert cast(Any, response.is_closed) is True
