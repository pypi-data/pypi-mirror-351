# ruff: noqa: ARG001
import asyncio
import os
import time

import pytest
from futurehouse_client.clients import (
    JobNames,
)
from futurehouse_client.clients.rest_client import RestClient, TaskFetchError
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
    with pytest.raises(TaskFetchError) as exc_info:
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
