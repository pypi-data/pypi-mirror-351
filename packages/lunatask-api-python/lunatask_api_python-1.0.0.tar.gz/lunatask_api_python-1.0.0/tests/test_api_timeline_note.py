"""Test Person Timeline Note APIs."""

# ruff: noqa: D103, S101

import datetime
import uuid
from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from tests import mock_requests
from tests.test_config import TEST_LUNATASK_API_TOKEN, TEST_UUID


def test_create_timeline_note() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.create_timeline_note(
        TEST_UUID, datetime.datetime.now(datetime.UTC), "note"
    )
    # https://lunatask.app/api/person-timeline-notes-api/create#response
    assert result.id == uuid.UUID(hex="6aa0d6e8-3b07-40a2-ae46-1bc272a0f472")
    assert result.date_on == datetime.datetime.fromisoformat("2021-01-10")
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")


def test_create_timeline_note_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_timeline_note(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.FORBIDDEN
