"""Test People APIs."""

# ruff: noqa: D103, S101

import datetime
import uuid
from http import HTTPStatus

import pytest
from requests import HTTPError, RequestException

from lunatask import api
from lunatask.models import people, source
from tests import mock_requests
from tests.data.sample_people import dict_newperson_no_optional
from tests.test_config import TEST_LUNATASK_API_TOKEN, TEST_UUID


def test_create_person() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.create_person(
        people.NewPerson.from_dict(dict_newperson_no_optional)
    )
    # https://lunatask.app/api/people-api/create-person#response
    assert result.id == uuid.UUID(hex="5999b945-b2b1-48c6-aa72-b251b75b3c2e")
    assert result.relationship_strength == people.Relationship.BUSINESS_CONTACTS
    assert result.sources[0].source == "salesforce"
    assert result.sources[0].source_id == "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")


def test_create_person_custom_fields() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_person(
            people.NewPerson.from_dict(dict_newperson_no_optional), {"custom": "field"}
        )

    assert ex.type is RequestException
    assert ex.value.response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_create_person_duplicate() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_person(
            people.NewPerson.from_dict(dict_newperson_no_optional),
            {"duplicate": "true"},
        )

    assert ex.type is RequestException
    assert ex.value.response.status_code == HTTPStatus.NO_CONTENT


def test_create_person_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.create_person(
            people.NewPerson.from_dict(dict_newperson_no_optional)
        )

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.FORBIDDEN


def test_delete_person() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.delete_person(TEST_UUID)
    # https://lunatask.app/api/people-api/delete#response
    assert result.id == uuid.UUID(hex="5999b945-b2b1-48c6-aa72-b251b75b3c2e")
    assert result.relationship_strength == people.Relationship.BUSINESS_CONTACTS
    assert result.sources[0].source == "salesforce"
    assert result.sources[0].source_id == "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T12:52:04Z")
    assert result.deleted_at == datetime.datetime.fromisoformat("2021-01-10T12:52:04Z")


def test_delete_person_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.delete_person(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND


def test_get_person() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.get_person(TEST_UUID)
    # https://lunatask.app/api/people-api/list#response
    assert result.id == uuid.UUID(hex="5999b945-b2b1-48c6-aa72-b251b75b3c2e")
    assert result.relationship_strength == people.Relationship.BUSINESS_CONTACTS
    assert result.sources[0].source == "salesforce"
    assert result.sources[0].source_id == "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7"
    with pytest.raises(IndexError):
        assert result.sources[1]
    assert result.created_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")
    assert result.updated_at == datetime.datetime.fromisoformat("2021-01-10T10:39:25Z")


def test_get_person_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.get_person(TEST_UUID)

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND


def test_get_people() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests

    result = test_api.get_people(source.Source("hello", "world"))
    # https://lunatask.app/api/people-api/list#response
    assert result[0].id == uuid.UUID(hex="5999b945-b2b1-48c6-aa72-b251b75b3c2e")
    assert result[0].relationship_strength == people.Relationship.BUSINESS_CONTACTS
    assert result[0].sources[0].source == "salesforce"
    assert result[0].sources[0].source_id == "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7"
    with pytest.raises(IndexError):
        assert result[0].sources[1]
    assert result[0].created_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )
    assert result[0].updated_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )

    assert result[1].id == uuid.UUID(hex="109cbf01-dba9-4136-8cf1-a02084ba3977")
    assert result[1].relationship_strength == people.Relationship.FAMILY
    with pytest.raises(IndexError):
        assert result[1].sources[0]
    assert result[1].created_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )
    assert result[1].updated_at == datetime.datetime.fromisoformat(
        "2021-01-10T10:39:25Z"
    )

    with pytest.raises(IndexError):
        assert result[2]


def test_get_people_fail() -> None:
    test_api = api.LunataskAPI(TEST_LUNATASK_API_TOKEN)
    test_api._requests = mock_requests
    test_api.request_headers["fail"] = True

    with pytest.raises(RequestException) as ex:
        _ = test_api.get_people()

    assert ex.type is HTTPError
    assert ex.value.response.status_code == HTTPStatus.NOT_FOUND
