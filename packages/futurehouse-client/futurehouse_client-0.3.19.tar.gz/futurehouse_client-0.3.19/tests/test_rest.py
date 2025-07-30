# ruff: noqa: ARG001
# ruff:  noqa: SIM117
# pylint: disable=too-many-lines,import-error,too-many-public-methods
import asyncio
import os
import tempfile
import time
import types
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from futurehouse_client.clients import (
    JobNames,
)
from futurehouse_client.clients.rest_client import (
    FileUploadError,
    RestClient,
    RestClientError,
)
from futurehouse_client.models.app import (
    PhoenixTaskResponse,
    PQATaskResponse,
    Stage,
    TaskRequest,
    TaskResponseVerbose,
)
from futurehouse_client.models.rest import ExecutionStatus
from pytest_subtests import SubTests

ADMIN_API_KEY = os.environ["PLAYWRIGHT_ADMIN_API_KEY"]
PUBLIC_API_KEY = os.environ["PLAYWRIGHT_PUBLIC_API_KEY"]
TEST_MAX_POLLS = 100


@pytest.fixture
def admin_client():
    """Create a RestClient for testing; using an admin key."""
    return RestClient(
        stage=Stage.DEV,
        api_key=ADMIN_API_KEY,
    )


@pytest.fixture
def pub_client():
    """Create a RestClient for testing; using a public user key with limited access."""
    return RestClient(
        stage=Stage.DEV,
        api_key=PUBLIC_API_KEY,
    )


@pytest.fixture
def task_req():
    """Create a sample task request."""
    return TaskRequest(
        name=JobNames.from_string("dummy"),
        query="How many moons does earth have?",
    )


@pytest.fixture
def pqa_task_req():
    return TaskRequest(
        name=JobNames.from_string("crow"),
        query="How many moons does earth have?",
    )


@pytest.fixture
def phoenix_task_req():
    return TaskRequest(
        name=JobNames.from_string("phoenix"),
        query="What is the molecular weight of ascorbic acids?",
    )


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_futurehouse_dummy_env_crow(admin_client: RestClient, task_req: TaskRequest):
    admin_client.create_task(task_req)
    while (task_status := admin_client.get_task().status) in {"queued", "in progress"}:
        time.sleep(5)
    assert task_status == "success"


def test_insufficient_permissions_request(
    pub_client: RestClient, task_req: TaskRequest
):
    # Create a new instance so that cached credentials aren't reused
    with pytest.raises(PermissionError) as exc_info:
        pub_client.create_task(task_req)

    assert "Error creating task" in str(exc_info.value)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_job_response(  # noqa: PLR0915
    subtests: SubTests,
    admin_client: RestClient,
    pqa_task_req: TaskRequest,
    phoenix_task_req: TaskRequest,
):
    task_id = admin_client.create_task(pqa_task_req)
    atask_id = await admin_client.acreate_task(pqa_task_req)
    phoenix_task_id = admin_client.create_task(phoenix_task_req)
    aphoenix_task_id = await admin_client.acreate_task(phoenix_task_req)

    with subtests.test("Test TaskResponse with queued task"):
        task_response = admin_client.get_task(task_id)
        assert task_response.status in {"queued", "in progress"}
        assert task_response.job_name == pqa_task_req.name
        assert task_response.query == pqa_task_req.query
        task_response = await admin_client.aget_task(atask_id)
        assert task_response.status in {"queued", "in progress"}
        assert task_response.job_name == pqa_task_req.name
        assert task_response.query == pqa_task_req.query

    for _ in range(TEST_MAX_POLLS):
        task_response = admin_client.get_task(task_id)
        if task_response.status in ExecutionStatus.terminal_states():
            break
        await asyncio.sleep(5)

    for _ in range(TEST_MAX_POLLS):
        task_response = await admin_client.aget_task(atask_id)
        if task_response.status in ExecutionStatus.terminal_states():
            break
        await asyncio.sleep(5)

    with subtests.test("Test PQA job response"):
        task_response = admin_client.get_task(task_id)
        assert isinstance(task_response, PQATaskResponse)
        # assert it has general fields
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert pqa_task_req.name in task_response.job_name
        assert pqa_task_req.query in task_response.query
        # assert it has PQA specific fields
        assert task_response.answer is not None
        # assert it's not verbose
        assert not hasattr(task_response, "environment_frame")
        assert not hasattr(task_response, "agent_state")

    with subtests.test("Test async PQA job response"):
        task_response = await admin_client.aget_task(atask_id)
        assert isinstance(task_response, PQATaskResponse)
        # assert it has general fields
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert pqa_task_req.name in task_response.job_name
        assert pqa_task_req.query in task_response.query
        # assert it has PQA specific fields
        assert task_response.answer is not None
        # assert it's not verbose
        assert not hasattr(task_response, "environment_frame")
        assert not hasattr(task_response, "agent_state")

    with subtests.test("Test Phoenix job response"):
        task_response = admin_client.get_task(phoenix_task_id)
        assert isinstance(task_response, PhoenixTaskResponse)
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert phoenix_task_req.name in task_response.job_name
        assert phoenix_task_req.query in task_response.query

    with subtests.test("Test async Phoenix job response"):
        task_response = await admin_client.aget_task(aphoenix_task_id)
        assert isinstance(task_response, PhoenixTaskResponse)
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert phoenix_task_req.name in task_response.job_name
        assert phoenix_task_req.query in task_response.query

    with subtests.test("Test task response with verbose"):
        task_response = admin_client.get_task(task_id, verbose=True)
        assert isinstance(task_response, TaskResponseVerbose)
        assert task_response.status == "success"
        assert task_response.environment_frame is not None
        assert task_response.agent_state is not None

    with subtests.test("Test task async response with verbose"):
        task_response = await admin_client.aget_task(atask_id, verbose=True)
        assert isinstance(task_response, TaskResponseVerbose)
        assert task_response.status == "success"
        assert task_response.environment_frame is not None
        assert task_response.agent_state is not None


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_run_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = admin_client.run_tasks_until_done(tasks_to_do)

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status == "success" for task in results)


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
@pytest.mark.asyncio
async def test_arun_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = await admin_client.arun_tasks_until_done(tasks_to_do)

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status == "success" for task in results)


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
@pytest.mark.asyncio
async def test_timeout_run_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = await admin_client.arun_tasks_until_done(
        tasks_to_do, verbose=True, timeout=5, progress_bar=True
    )

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status != "success" for task in results), "Should not be success."
    assert all(not isinstance(task, PQATaskResponse) for task in results), (
        "Should be verbose."
    )

    results = admin_client.run_tasks_until_done(
        tasks_to_do, verbose=True, timeout=5, progress_bar=True
    )

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status != "success" for task in results), "Should not be success."
    assert all(not isinstance(task, PQATaskResponse) for task in results), (
        "Should be verbose."
    )


class TestParallelChunking:
    """Test suite for parallel chunk upload functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock RestClient for testing."""
        # we don't need a real RestClient auth here
        client = MagicMock(spec=RestClient)
        client.CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
        client.MAX_CONCURRENT_CHUNKS = 12
        client.multipart_client = MagicMock()

        # Set up the real methods we want to test by properly binding them
        client._upload_chunks_parallel = types.MethodType(
            RestClient._upload_chunks_parallel, client
        )
        client._upload_single_chunk = types.MethodType(
            RestClient._upload_single_chunk, client
        )
        client._upload_single_file = types.MethodType(
            RestClient._upload_single_file, client
        )
        client._upload_directory = types.MethodType(
            RestClient._upload_directory, client
        )
        client.upload_file = types.MethodType(RestClient.upload_file, client)
        client._wait_for_all_assemblies_completion = MagicMock(return_value=True)

        return client

    @pytest.fixture
    def large_file_content(self):
        """Create content for a large file that will be chunked."""
        # Create content larger than CHUNK_SIZE (16MB)
        chunk_size = 16 * 1024 * 1024
        return b"A" * (chunk_size * 2 + 1000)  # ~32MB + 1000 bytes

    @pytest.fixture
    def small_file_content(self):
        """Create content for a small file that won't be chunked."""
        return b"Small file content"

    def test_upload_small_file_no_chunking(self, mock_client):
        """Test uploading a small file that doesn't require chunking."""
        job_name = "test-job"
        file_content = b"Small file content"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Verify upload was called once (single chunk)
                assert mock_client.multipart_client.post.call_count == 1
                assert upload_id is not None

                # Verify the post call was made with correct endpoint
                call_args = mock_client.multipart_client.post.call_args
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call_args[0][0]
            finally:
                temp_path.unlink()

    def test_upload_large_file_with_chunking(self, mock_client, large_file_content):
        """Test uploading a large file that requires chunking and parallel uploads."""
        job_name = "test-job"

        # Mock successful responses for all chunks
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_response.status_code = 200
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(large_file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Verify multiple chunks were uploaded
                # File size: ~32MB + 1000 bytes, chunk size: 16MB
                # Expected chunks: 3 (16MB + 16MB + 1000 bytes)
                expected_chunks = 3
                assert mock_client.multipart_client.post.call_count == expected_chunks
                assert upload_id is not None

                # Verify all calls were to the upload-chunk endpoint
                for call in mock_client.multipart_client.post.call_args_list:
                    assert f"/v0.1/crows/{job_name}/upload-chunk" in call[0][0]
            finally:
                temp_path.unlink()

    def test_upload_chunks_parallel_batch_processing(self, mock_client):
        """Test that chunks are processed in parallel batches."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        num_regular_chunks = 5  # Smaller number for easier testing
        total_chunks = 6

        # Mock file content for final chunk
        chunk_content = b"A" * 1000

        # Mock final chunk response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        # Use patch to mock the _upload_single_chunk method and file operations
        with patch.object(mock_client, "_upload_single_chunk") as mock_upload_chunk:
            with patch("builtins.open", mock_open(read_data=chunk_content)):
                with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                    mock_temp_file.return_value.__enter__.return_value.name = (
                        "temp_chunk"
                    )

                    # Call the method - it should use ThreadPoolExecutor internally
                    mock_client._upload_chunks_parallel(
                        job_name,
                        file_path,
                        file_name,
                        upload_id,
                        total_chunks,
                    )

            # Verify all regular chunks were processed by checking the call count
            assert mock_upload_chunk.call_count == num_regular_chunks

            # Verify the calls were made with correct parameters
            for call_idx, call in enumerate(mock_upload_chunk.call_args_list):
                args = call[0]
                assert args[0] == job_name
                assert args[1] == file_path
                assert args[2] == file_name
                assert args[3] == upload_id
                assert args[4] == call_idx  # chunk_index
                assert args[5] == total_chunks

    def test_upload_single_chunk_success(self, mock_client):
        """Test successful upload of a single chunk."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        chunk_index = 0
        total_chunks = 5

        # Mock file content
        chunk_content = b"A" * mock_client.CHUNK_SIZE

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client.multipart_client.post.return_value = mock_response

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                # Setup mock temporary file
                mock_temp_file.return_value.__enter__.return_value.name = "temp_chunk"

                mock_client._upload_single_chunk(
                    job_name, file_path, file_name, upload_id, chunk_index, total_chunks
                )

                # Verify the upload was called with correct parameters
                mock_client.multipart_client.post.assert_called_once()
                call_args = mock_client.multipart_client.post.call_args

                # Check endpoint
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call_args[0][0]

                # Check data parameters
                data = call_args[1]["data"]
                assert data["file_name"] == file_name
                assert data["chunk_index"] == chunk_index
                assert data["total_chunks"] == total_chunks
                assert data["upload_id"] == upload_id

    def test_upload_chunks_parallel_retry_on_conflict(self, mock_client):
        """Test final chunk upload with retry logic for missing chunks (409 conflict)."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        total_chunks = 1

        # Mock file content
        chunk_content = b"A" * 1000

        # Create mock responses: first returns 409 (conflict), second succeeds
        mock_response_conflict = MagicMock()
        mock_response_conflict.status_code = 409  # CONFLICT
        mock_response_conflict.raise_for_status.side_effect = None

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            "status_url": "http://test.com/status"
        }

        mock_client.multipart_client.post.side_effect = [
            mock_response_conflict,
            mock_response_success,
        ]

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                with patch("time.sleep") as mock_sleep:  # Speed up test
                    mock_temp_file.return_value.__enter__.return_value.name = (
                        "temp_chunk"
                    )

                    status_url = mock_client._upload_chunks_parallel(
                        job_name,
                        file_path,
                        file_name,
                        upload_id,
                        total_chunks,
                    )

                    # Verify retry was attempted
                    assert mock_client.multipart_client.post.call_count == 2
                    assert status_url == "http://test.com/status"
                    mock_sleep.assert_called_once()  # Verify sleep was called for retry

    def test_upload_chunks_parallel_final_chunk_max_retries_exceeded(self, mock_client):
        """Test final chunk upload fails after max retries."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        total_chunks = 1

        # Mock file content
        chunk_content = b"A" * 1000

        # Create a side effect that simulates an exception on every attempt
        def side_effect(*args, **kwargs):
            raise Exception("Simulated upload failure")  # noqa: TRY002

        mock_client.multipart_client.post.side_effect = side_effect

        from httpx import codes

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                with patch("time.sleep"):  # Speed up test
                    # Set up the code constant correctly
                    with patch("futurehouse_client.clients.rest_client.codes", codes):
                        mock_temp_file.return_value.__enter__.return_value.name = (
                            "temp_chunk"
                        )

                        with pytest.raises(
                            FileUploadError, match="Error uploading final chunk"
                        ):
                            mock_client._upload_chunks_parallel(
                                job_name,
                                file_path,
                                file_name,
                                upload_id,
                                total_chunks,
                            )

                # Verify that retries were attempted (should be 3 attempts total)
                assert mock_client.multipart_client.post.call_count == 3

    def test_upload_directory_recursive(self, mock_client):
        """Test uploading a directory with nested files."""
        job_name = "test-job"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            (temp_path / "subdir").mkdir()
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.txt").write_text("content2")
            (temp_path / "subdir" / "file3.txt").write_text("content3")

            # Mock assembly completion
            with patch.object(
                mock_client, "_wait_for_all_assemblies_completion", return_value=True
            ):
                upload_id_result = mock_client.upload_file(job_name, temp_path)

            # Verify files were uploaded (3 files total)
            assert mock_client.multipart_client.post.call_count == 3
            # Just check that we got some upload_id back (it will be a UUID)
            assert upload_id_result is not None
            assert len(upload_id_result) > 0

            # Verify calls were made to upload-chunk endpoint
            for call in mock_client.multipart_client.post.call_args_list:
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call[0][0]

    def test_upload_file_assembly_failure(self, mock_client):
        """Test upload_file raises error when assembly fails."""
        job_name = "test-job"
        file_content = b"test content"

        # Mock successful upload but failed assembly
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly failure
                with (
                    patch.object(
                        mock_client,
                        "_wait_for_all_assemblies_completion",
                        return_value=False,
                    ),
                    pytest.raises(
                        RestClientError, match="Assembly failed or timed out"
                    ),
                ):
                    mock_client.upload_file(job_name, temp_path)
            finally:
                temp_path.unlink()

    def test_upload_file_skip_assembly_wait(self, mock_client):
        """Test upload_file with wait_for_assembly=False."""
        job_name = "test-job"
        file_content = b"test content"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                with patch.object(
                    mock_client, "_wait_for_all_assemblies_completion"
                ) as mock_wait:
                    upload_id = mock_client.upload_file(
                        job_name, temp_path, wait_for_assembly=False
                    )

                    # Verify assembly wait was not called
                    mock_wait.assert_not_called()
                    assert upload_id is not None
            finally:
                temp_path.unlink()

    def test_max_concurrent_chunks_constant(self, mock_client):
        """Test that MAX_CONCURRENT_CHUNKS constant is properly set."""
        assert mock_client.MAX_CONCURRENT_CHUNKS == 12
        assert isinstance(mock_client.MAX_CONCURRENT_CHUNKS, int)
        assert mock_client.MAX_CONCURRENT_CHUNKS > 0

    def test_upload_empty_file_handled(self, mock_client):
        """Test that empty files are handled gracefully."""
        job_name = "test-job"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create empty file
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Should not call post since empty files are skipped
                assert mock_client.multipart_client.post.call_count == 0
                assert upload_id is not None
            finally:
                temp_path.unlink()

    def test_chunk_size_calculation(self, mock_client):
        """Test that chunk size calculation works correctly."""
        file_size = 32 * 1024 * 1024 + 1000  # 32MB + 1000 bytes
        chunk_size = mock_client.CHUNK_SIZE  # 16MB

        expected_total_chunks = (file_size + chunk_size - 1) // chunk_size
        assert expected_total_chunks == 3  # 16MB + 16MB + ~1000 bytes

        # Test edge cases
        assert (
            (chunk_size - 1) + chunk_size - 1
        ) // chunk_size == 1  # Just under 1 chunk
        assert (chunk_size + chunk_size - 1) // chunk_size == 1  # Exactly 1 chunk
        assert (
            (chunk_size + 1) + chunk_size - 1
        ) // chunk_size == 2  # Just over 1 chunk
