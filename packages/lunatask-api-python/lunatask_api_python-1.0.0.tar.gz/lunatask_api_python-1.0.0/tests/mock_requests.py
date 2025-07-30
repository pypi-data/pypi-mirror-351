"""Mocking a partial 'requests' API."""

# ruff: noqa: D101, D102, S101

import re
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Final

# RequestException needs to be in here, even though it's not explicitly used
# in here. The API methods will need it.
from requests import HTTPError, RequestException, Response  # noqa: F401

# Valid/known API URL patterns.
REQUEST_URL_PATTERN: Final[re.Pattern] = re.compile(
    r"^https://api\.lunatask\.app/v1/(?P<target>habits|notes|people|person_timeline_notes|ping|tasks)/?(?P<uuid>[-0123456789abcdefABCDEF]{36})?(?P<track>/track)?.*$"
)


@dataclass
class MockResponse:
    status_code: int
    the_json: dict[str, Any] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.the_json

    def raise_for_status(self) -> None:
        if self.status_code != HTTPStatus.OK:
            fake_response = Response()
            fake_response.status_code = self.status_code
            raise HTTPError(response=fake_response)


def _normalize_url(url: str) -> str:
    """Replace UUIDs with the string "id"."""
    pat = REQUEST_URL_PATTERN.match(url)
    if pat:
        groupdict = pat.groupdict()

        url = groupdict["target"]

        if groupdict.get("uuid"):
            url += "/id"

        if groupdict["target"] == "habits" and groupdict.get("track"):
            url += "/track"

    return url


def delete(url: str, **kwargs: dict[str, Any] | None) -> MockResponse:
    """Fake DELETE method.

    Possible DELETE requests on these URLs:

    f"{API_ENDPOINT}/people/{person_id}" - Delete a person
    f"{API_ENDPOINT}/tasks/{task_id}" - Delete task
    """
    response = MockResponse(status_code=HTTPStatus.OK)

    op = _normalize_url(url)
    match op:
        case "people/id":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "person": {
                        "id": "5999b945-b2b1-48c6-aa72-b251b75b3c2e",
                        "relationship_strength": "business-contacts",
                        "sources": [
                            {
                                "source": "salesforce",
                                "source_id": "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7",
                            }
                        ],
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T12:52:04Z",
                        "deleted_at": "2021-01-10T12:52:04Z",
                    }
                }

        case "tasks/id":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "task": {
                        "id": "066b5835-184f-4fd9-be60-7d735aa94708",
                        "area_id": "11b37775-5a34-41bb-b109-f0e5a6084799",
                        "goal_id": None,
                        "status": "later",
                        "previous_status": None,
                        "estimate": None,
                        "priority": 0,
                        "progress": None,
                        "motivation": "unknown",
                        "eisenhower": 0,
                        "sources": [],
                        "scheduled_on": None,
                        "completed_at": None,
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T12:52:04Z",
                        "deleted_at": "2021-01-10T12:52:04Z",
                    }
                }

        case _:
            raise HTTPError(HTTPStatus.NOT_IMPLEMENTED)

    return response


def get(  # noqa: PLR0912
    url: str, params: dict[str, Any] | None = None, **kwargs: dict[str, Any] | None
) -> MockResponse:
    """Fake GET method.

    Possible GET requests on these URLs:

    f"{API_ENDPOINT}/people" - Get all people
    f"{API_ENDPOINT}/people/{person_id}" - Get a specific person
    f"{API_ENDPOINT}/ping" - Authentication example
    f"{API_ENDPOINT}/tasks" - Get all tasks
    f"{API_ENDPOINT}/tasks/{task_id}" - Get specific task
    """
    response = MockResponse(status_code=HTTPStatus.OK)

    op = _normalize_url(url)
    match op:
        case "people":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "people": [
                        {
                            "id": "5999b945-b2b1-48c6-aa72-b251b75b3c2e",
                            "relationship_strength": "business-contacts",
                            "sources": [
                                {
                                    "source": "salesforce",
                                    "source_id": "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7",
                                }
                            ],
                            "created_at": "2021-01-10T10:39:25Z",
                            "updated_at": "2021-01-10T10:39:25Z",
                        },
                        {
                            "id": "109cbf01-dba9-4136-8cf1-a02084ba3977",
                            "relationship_strength": "family",
                            "sources": [],
                            "created_at": "2021-01-10T10:39:25Z",
                            "updated_at": "2021-01-10T10:39:25Z",
                        },
                    ]
                }

        case "people/id":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "person": {
                        "id": "5999b945-b2b1-48c6-aa72-b251b75b3c2e",
                        "relationship_strength": "business-contacts",
                        "sources": [
                            {
                                "source": "salesforce",
                                "source_id": "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7",
                            }
                        ],
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                    }
                }

        case "ping":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.IM_A_TEAPOT
            else:
                response.the_json = {"message": "pong"}

        case "tasks":
            if "source" in params:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "tasks": [
                        {
                            "id": "066b5835-184f-4fd9-be60-7d735aa94708",
                            "area_id": "11b37775-5a34-41bb-b109-f0e5a6084799",
                            "goal_id": None,
                            "status": "next",
                            "previous_status": "later",
                            "estimate": 10,
                            "priority": 0,
                            "progress": 25,
                            "motivation": "unknown",
                            "eisenhower": 0,
                            "sources": [{"source": "github", "source_id": "123"}],
                            "scheduled_on": None,
                            "completed_at": None,
                            "created_at": "2021-01-10T10:39:25Z",
                            "updated_at": "2021-01-10T10:39:25Z",
                            "deleted_at": None,
                        },
                        {
                            "id": "0e0cff5c-c334-4a24-b15a-4fca6cfbf25f",
                            "area_id": "f557287e-ae43-4472-9478-497887362dcb",
                            "goal_id": None,
                            "status": "later",
                            "previous_status": None,
                            "estimate": 120,
                            "priority": 0,
                            "motivation": "unknown",
                            "eisenhower": 0,
                            "progress": None,
                            "sources": [],
                            "scheduled_on": None,
                            "completed_at": None,
                            "created_at": "2021-01-10T10:39:26Z",
                            "updated_at": "2021-01-10T10:39:26Z",
                            "deleted_at": None,
                        },
                    ]
                }

        case "tasks/id":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "task": {
                        "id": "066b5835-184f-4fd9-be60-7d735aa94708",
                        "area_id": "11b37775-5a34-41bb-b109-f0e5a6084799",
                        "goal_id": None,
                        "status": "next",
                        "previous_status": "later",
                        "estimate": 10,
                        "priority": 0,
                        "progress": None,
                        "motivation": "unknown",
                        "eisenhower": 0,
                        "sources": [{"source": "github", "source_id": "123"}],
                        "scheduled_on": None,
                        "completed_at": None,
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                        "deleted_at": None,
                    }
                }

        case _:
            raise HTTPError(HTTPStatus.NOT_IMPLEMENTED)

    return response


def post(  # noqa: PLR0912
    url: str,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    **kwargs: dict[str, Any] | None,
) -> MockResponse:
    """Fake POST method.

    Possible POST requests on these URLs:

    f"{API_ENDPOINT}/habits/{habit}/track" - Track a habit
    f"{API_ENDPOINT}/notes" - Create a note
    f"{API_ENDPOINT}/people" - Create a person
    f"{API_ENDPOINT}/tasks" - Create task
    """
    response = MockResponse(status_code=HTTPStatus.CREATED)

    op = _normalize_url(url)
    match op:
        case "habits/id/track":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.FORBIDDEN
            else:
                # https://tenor.com/en-CA/view/one-punch-man-ok-saitama-gif-4973579
                response.the_json = {"status": "ok"}

        case "notes":
            if json.get("name") == "duplicate":
                response.status_code = HTTPStatus.NO_CONTENT
            elif "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.FORBIDDEN
            else:
                response.the_json = {
                    "note": {
                        "id": "5999b945-b2b1-48c6-aa72-b251b75b3c2e",
                        "notebook_id": "d1ff35f5-6b25-4199-ab6e-c19fe3fe27f1",
                        "date_on": None,
                        "sources": [
                            {
                                "source": "evernote",
                                "source_id": "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7",
                            }
                        ],
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                        "deleted_at": None,
                    }
                }

        case "people":
            if json.get("custom"):
                response.status_code = HTTPStatus.UNPROCESSABLE_CONTENT
            elif json.get("duplicate"):
                response.status_code = HTTPStatus.NO_CONTENT
            elif "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.FORBIDDEN
            else:
                response.the_json = {
                    "person": {
                        "id": "5999b945-b2b1-48c6-aa72-b251b75b3c2e",
                        "relationship_strength": "business-contacts",
                        "sources": [
                            {
                                "source": "salesforce",
                                "source_id": "352fd2d7-cdc0-4e91-a0a3-9d6cc9d440e7",
                            }
                        ],
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                    }
                }

        case "person_timeline_notes":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.FORBIDDEN
            else:
                response.the_json = {
                    "person_timeline_note": {
                        "id": "6aa0d6e8-3b07-40a2-ae46-1bc272a0f472",
                        "date_on": "2021-01-10",
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                    }
                }

        case "tasks":
            if json.get("name") == "duplicate":
                response.status_code = HTTPStatus.NO_CONTENT
            elif json.get("name") == "teapot":
                response.status_code = HTTPStatus.IM_A_TEAPOT
            else:
                response.the_json = {
                    "task": {
                        "id": "066b5835-184f-4fd9-be60-7d735aa94708",
                        "area_id": "11b37775-5a34-41bb-b109-f0e5a6084799",
                        "goal_id": None,
                        "status": "later",
                        "previous_status": None,
                        "estimate": None,
                        "priority": 0,
                        "progress": None,
                        "motivation": "unknown",
                        "eisenhower": 0,
                        "sources": [{"source": "github", "source_id": "123"}],
                        "scheduled_on": None,
                        "completed_at": None,
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                    }
                }

        case _:
            raise HTTPError(HTTPStatus.NOT_IMPLEMENTED)

    return response


def put(
    url: str,
    data: dict[str, Any] | None = None,
    **kwargs: dict[str, Any] | None,
) -> MockResponse:
    """Fake PUT method.

    Possible PUT requests on these URLs:

    f"{API_ENDPOINT}/tasks/{task_id}" - Update task
    """
    response = MockResponse(status_code=HTTPStatus.OK)

    op = _normalize_url(url)
    match op:
        case "tasks/id":
            if "fail" in kwargs["headers"]:
                response.status_code = HTTPStatus.NOT_FOUND
            else:
                response.the_json = {
                    "task": {
                        "id": "066b5835-184f-4fd9-be60-7d735aa94708",
                        "area_id": "11b37775-5a34-41bb-b109-f0e5a6084799",
                        "goal_id": None,
                        "status": "later",
                        "previous_status": None,
                        "estimate": None,
                        "priority": None,
                        "progress": None,
                        "motivation": "must",
                        "eisenhower": 0,
                        "sources": [],
                        "scheduled_on": None,
                        "completed_at": None,
                        "created_at": "2021-01-10T10:39:25Z",
                        "updated_at": "2021-01-10T10:39:25Z",
                        "deleted_at": None,
                    }
                }

        case _:
            response.status_code = HTTPStatus.NOT_IMPLEMENTED

    return response
