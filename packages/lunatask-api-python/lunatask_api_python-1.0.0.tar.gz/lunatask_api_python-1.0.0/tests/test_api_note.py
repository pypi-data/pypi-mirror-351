"""Test Note APIs."""

# ruff: noqa: D103, S101

import datetime
import uuid
from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from lunatask.models import source
from tests import mock_requests
from tests.test_config import TEST_LUNATASK_API_TOKEN, TEST_UUID


def test_create_note() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.create_note(
        TEST_UUID,
        "note",
        "content",
        datetime.datetime.now(datetime.UTC),
        source.Source("hello", "world"),
    )
    # https://lunatask.app/api/notes-api/create#response
    assert result.id == uuid.UUID(hex="5999b945-b2b1-48c6-aa72-b251b75b3c2e")
    assert result.notebook_id == uuid.UUID(hex="d1ff35f5-6b25-4199-ab6e-c19fe3fe27f1")
    assert result.date_on is None
    assert result.sources[0].source == "evernote"
    assert result.sources[0].source_id == "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.deleted_at is None


def test_create_note_duplicate() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_note(TEST_UUID, "duplicate", "content")

    assert ex.type is RequestException
    assert ex.value.response.status_code == HTTPStatus.NO_CONTENT


def test_create_note_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_note(TEST_UUID, "note", "content")

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.FORBIDDEN
