"""Test Task APIs."""

# ruff: noqa: D103, S101

import datetime
import uuid
from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from lunatask.models import source, task
from tests import mock_requests
from tests.data.sample_task import dict_newtask_no_optional, dict_task_no_optional
from tests.test_config import TEST_LUNATASK_API_TOKEN, TEST_UUID


def test_create_task() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.create_task(
        task.NewTask.from_dict(dict_newtask_no_optional),
        source.Source("hello", "world"),
    )
    # https://lunatask.app/api/tasks-api/create#response
    assert result.id == uuid.UUID(hex="066b5835-184f-4fd9-be60-7d735aa94708")
    assert result.area_id == uuid.UUID(hex="11b37775-5a34-41bb-b109-f0e5a6084799")
    assert result.goal_id is None
    assert result.status == task.Status.LATER
    assert result.previous_status is None
    assert result.estimate is None
    assert result.priority is task.Priority.NORMAL
    assert result.progress is None
    assert result.motivation is task.Motivation.UNKNOWN
    assert result.eisenhower is task.Eisenhower.UNCATEGORIZED
    assert result.sources[0].source == "github"
    assert result.sources[0].source_id == "123"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.scheduled_on is None
    assert result.completed_at is None
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")


def test_create_task_duplicate() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    duplicate_dict = dict_newtask_no_optional.copy()
    duplicate_dict["name"] = "duplicate"

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_task(task.NewTask.from_dict(duplicate_dict), None)

    assert ex.type is RequestException
    assert ex.value.response.status_code == HTTPStatus.NO_CONTENT


def test_create_task_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    fail_dict = dict_newtask_no_optional.copy()
    fail_dict["name"] = "teapot"

    with pytest.raises(HTTPError) as ex:
        _ = test_api.create_task(task.NewTask.from_dict(fail_dict), None)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.IM_A_TEAPOT

    fail_dict = dict_newtask_no_optional.copy()
    fail_dict["source"] = "This will fail."
    fail_dict["source_id"] = None

    with pytest.raises(source.MissingSourceIdError):
        _ = test_api.create_task(task.NewTask.from_dict(fail_dict))

    with pytest.raises(source.MissingSourceIdError):
        _ = test_api.create_task(
            task.NewTask.from_dict(dict_newtask_no_optional),
            source.Source("This will fail."),
        )


def test_delete_task() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.delete_task(TEST_UUID)
    # https://lunatask.app/api/tasks-api/delete#response
    assert result.id == uuid.UUID(hex="066b5835-184f-4fd9-be60-7d735aa94708")
    assert result.area_id == uuid.UUID(hex="11b37775-5a34-41bb-b109-f0e5a6084799")
    assert result.goal_id is None
    assert result.status == task.Status.LATER
    assert result.previous_status is None
    assert result.estimate is None
    assert result.priority is task.Priority.NORMAL
    assert result.progress is None
    assert result.motivation is task.Motivation.UNKNOWN
    assert result.eisenhower is task.Eisenhower.UNCATEGORIZED
    assert not result.sources
    assert result.scheduled_on is None
    assert result.completed_at is None
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T12:52:04Z")
    assert result.deleted_at == datetime.datetime.fromisoformat("2021-01-10T12:52:04Z")


def test_delete_task_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.delete_task(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND


def test_get_task() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.get_task(TEST_UUID)
    # https://lunatask.app/api/tasks-api/show#response
    assert result.id == uuid.UUID(hex="066b5835-184f-4fd9-be60-7d735aa94708")
    assert result.area_id == uuid.UUID(hex="11b37775-5a34-41bb-b109-f0e5a6084799")
    assert result.goal_id is None
    assert result.status == task.Status.NEXT
    assert result.previous_status == task.Status.LATER
    assert result.estimate == 10  # noqa: PLR2004
    assert result.priority is task.Priority.NORMAL
    assert result.progress is None
    assert result.motivation is task.Motivation.UNKNOWN
    assert result.eisenhower is task.Eisenhower.UNCATEGORIZED
    assert result.sources[0].source == "github"
    assert result.sources[0].source_id == "123"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.scheduled_on is None
    assert result.completed_at is None
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")


def test_get_task_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.get_task(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND


def test_get_tasks() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.get_tasks()
    # https://lunatask.app/api/tasks-api/list#response
    assert result[0].id == uuid.UUID(hex="066b5835-184f-4fd9-be60-7d735aa94708")
    assert result[0].area_id == uuid.UUID(hex="11b37775-5a34-41bb-b109-f0e5a6084799")
    assert result[0].goal_id is None
    assert result[0].status == task.Status.NEXT
    assert result[0].previous_status == task.Status.LATER
    assert result[0].estimate == 10  # noqa: PLR2004
    assert result[0].priority == task.Priority.NORMAL
    assert result[0].progress == 25  # noqa: PLR2004
    assert result[0].motivation == task.Motivation.UNKNOWN
    assert result[0].eisenhower == task.Eisenhower.UNCATEGORIZED
    assert result[0].sources[0].source == "github"
    assert result[0].sources[0].source_id == "123"
    with pytest.raises(IndexError):
        assert result[0].sources[1]
    assert result[0].scheduled_on is None
    assert result[0].completed_at is None
    assert result[0].created_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )
    assert result[0].updated_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )
    assert result[0].deleted_at is None

    assert result[1].id == uuid.UUID(hex="0e0cff5c-c334-4a24-b15a-4fca6cfbf25f")
    assert result[1].area_id == uuid.UUID(hex="f557287e-ae43-4472-9478-497887362dcb")
    assert result[1].goal_id is None
    assert result[1].status == task.Status.LATER
    assert result[1].previous_status is None
    assert result[1].estimate == 120  # noqa: PLR2004
    assert result[1].priority == task.Priority.NORMAL
    assert result[1].motivation == task.Motivation.UNKNOWN
    assert result[1].eisenhower == task.Eisenhower.UNCATEGORIZED
    assert result[1].progress is None
    assert not result[1].sources
    assert result[1].scheduled_on is None
    assert result[1].completed_at is None
    assert result[1].created_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:26Z"
    )
    assert result[1].updated_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:26Z"
    )
    assert result[1].deleted_at is None

    with pytest.raises(IndexError):
        assert result[2]


def test_get_tasks_filtering() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    with pytest.raises(RequestException) as ex:
        _ = test_api.get_tasks(source.Source("hello", "world"))

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND


def test_update_task() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.update_task(
        task.Task.from_dict(dict_task_no_optional), "Name", "Note"
    )
    # https://lunatask.app/api/tasks-api/update#response
    assert result.id == uuid.UUID(hex="066b5835-184f-4fd9-be60-7d735aa94708")
    assert result.area_id == uuid.UUID(hex="11b37775-5a34-41bb-b109-f0e5a6084799")
    assert result.goal_id is None
    assert result.status == task.Status.LATER
    assert result.previous_status is None
    assert result.estimate is None
    assert result.priority is None
    assert result.progress is None
    assert result.motivation == task.Motivation.MUST
    assert result.eisenhower == task.Eisenhower.UNCATEGORIZED
    assert not result.sources
    assert result.scheduled_on is None
    assert result.completed_at is None
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.deleted_at is None


def test_update_task_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.update_task(task.Task.from_dict(dict_task_no_optional))

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND
