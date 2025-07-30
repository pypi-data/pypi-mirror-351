"""Test Ping API."""

# ruff: noqa: D103, S101

from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from tests import mock_requests
from tests.test_config import TEST_LUNATASK_API_TOKEN


def test_ping() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    ping = test_api.ping()

    assert ping == "pong"


def test_ping_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.ping()

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.IM_A_TEAPOT
