"""Test Habit API."""

# ruff: noqa: D103, S101

import datetime
from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from tests import mock_requests
from tests.test_config import TEST_LUNATASK_API_TOKEN, TEST_UUID


def test_track_habit() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    _ = test_api.track_habit(TEST_UUID)
    # https://lunatask.app/api/habits-api/track-activity#response


def test_track_habit_date() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    _ = test_api.track_habit(TEST_UUID, datetime.datetime.now(datetime.UTC))
    # https://lunatask.app/api/habits-api/track-activity#response


def test_track_habit_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.track_habit(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.FORBIDDEN
    # https://lunatask.app/api/habits-api/track-activity#response
