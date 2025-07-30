"""Lunatask API class.

This API conforms to v1 of Luntask's API: <https://lunatask.app/api/overview>

To use this you must have a Lunatask API token. In the desktop app:

1. Click the Settings icon ⚙️ in the top left.
2. Click "Access tokens" in the Preferences list on the lef.
3. Click the "Create access token" button. Rename it to something like
    "Todoist Import" so you don't forget what it's for.
4. Click the "Copy to clipboard" button and paste it into your code.

This is modelled loosely on the Todoist API:
<https://pypi.org/project/todoist-api-python/>
"""

import datetime
from http import HTTPStatus
from types import ModuleType
from typing import Final, Self
from uuid import UUID

import requests

from config import LUNATASK_API_TOKEN_LENGTH, TokenLengthError
from lunatask.models.note import Note
from lunatask.models.people import NewPerson, Person
from lunatask.models.source import MissingSourceIdError, Source
from lunatask.models.task import NewTask, Task
from lunatask.models.timeline_note import TimelineNote

# Base API endpoint.
API_ENDPOINT: Final[str] = "https://api.lunatask.app/v1"

# Request timeout for (connection, response) times, in seconds.
#
# Lunatask doesn't document how long its API lets requests run before timing
# out; 10s for a connection and 60s to get a response are recommendations from
# the requests library, and they're what Todoist's API uses.
API_TIMEOUT: Final[tuple[int, int]] = (10, 60)


class LunataskAPI:
    """Lunatask API object.

    Create one of these to interact with Lunatask's API. The methods conform
    to the various APIs available in Lunatask's API.
    """

    # Lunatask API token; see config.py for requirements.
    api_token: str

    # requests module timeout value(s) in seconds. If a
    api_timeout: tuple[int | float, int | float] | float

    # HTTP requests module. Exposed for testing.
    _requests: ModuleType = requests

    def __init__(
        self: Self,
        api_token: str,
        api_timeout: tuple[int | float, int | float] | float = API_TIMEOUT,
    ) -> None:
        """Create a LunataskAPI instance using the given API token.

        Arguments:
        * `api_token` - A Lunatask API token. Default:
          `https://api.lunatask.app/v1`
        * `api_timeout` - A timeout value or tuple of (connect timeout, read
          timeout) in seconds; see the requests docs for details.
          Default: `(10, 60)`
        """
        if len(api_token) != LUNATASK_API_TOKEN_LENGTH:
            raise TokenLengthError

        self.api_token = api_token
        self.api_timeout = api_timeout
        self.request_headers = {"Authorization": f"bearer {api_token}"}

    ###########################################################################
    # Ping API
    ###########################################################################

    def ping(self: Self) -> str:
        """Ping the server to test your API token.

        <https://lunatask.app/api/authentication>

        Returns:
        * "pong" for success.
        """
        response = self._requests.get(
            f"{API_ENDPOINT}/ping",
            headers=self.request_headers,
            timeout=self.api_timeout,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        json = response.json()
        return json["message"]

    ###########################################################################
    # Task APIs
    ###########################################################################

    def create_task(
        self: Self, new_task: NewTask, source: Source | None = None
    ) -> Task:
        """Create a new task.

        Throws `RequestException` if you're creating a duplicate task
        (a task with the same `area_id`, `source`, and `source_id` already
        exists and isn't `Completed`). The exception's `response.status_code`
        will be `NO_CONTENT`.

        <https://lunatask.app/api/tasks-api/create>

        Arguments:
        * `new_task` - The [`NewTask`](#pydoc:lunatask.models.task.NewTask) to
          use to create the `Task`.
        * `source` - An optional [`Source`](#pydoc:lunatask.models.source.Source)
          for the new `Task`.

        Returns:
        The newly created [`Task`](#pydoc:lunatask.models.task.Task).
        """
        if new_task.source and not new_task.source_id:
            raise MissingSourceIdError

        if source:
            new_task.source = source.source
            if source.source_id is None:
                raise MissingSourceIdError
            new_task.source_id = source.source_id

        response = self._requests.post(
            f"{API_ENDPOINT}/tasks",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=new_task.to_dict(),
        )

        if response.status_code not in [HTTPStatus.CREATED, HTTPStatus.NO_CONTENT]:
            response.raise_for_status()

        if response.status_code == HTTPStatus.NO_CONTENT:
            raise self._requests.RequestException(response=response)

        response_json = response.json()
        return Task.from_dict(response_json["task"])

    def delete_task(self: Self, task_id: UUID) -> Task:
        """Delete the specified task.

        https://lunatask.app/api/tasks-api/delete

        Arguments:
        * `task_id` - A [`Task`](#pydoc:lunatask.models.task.Task)'s UUID.

        Returns:
        The deleted [`Task`](#pydoc:lunatask.models.task.Task).
        """
        response = self._requests.delete(
            f"{API_ENDPOINT}/tasks/{task_id}",
            headers=self.request_headers,
            timeout=self.api_timeout,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return Task.from_dict(response_json["task"])

    def get_task(self: Self, task_id: UUID) -> Task:
        """Get the specified task.

        <https://lunatask.app/api/tasks-api/show>

        Arguments:
        * `task_id` - A [`Task`](#pydoc:lunatask.models.task.Task)'s UUID.

        Returns:
        The deleted [`Task`](#pydoc:lunatask.models.task.Task).
        """
        response = self._requests.get(
            f"{API_ENDPOINT}/tasks/{task_id}",
            headers=self.request_headers,
            timeout=self.api_timeout,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return Task.from_dict(response_json["task"])

    def get_tasks(self: Self, source: Source | None = None) -> list[Task]:
        """Get all tasks.

        If `source` is specified, the result is limited to tasks from that
        source (with the `source_id` if one is specified), otherwise all tasks
        are returned.

        <https://lunatask.app/api/tasks-api/list>

        Arguments:
        * `source` - An optional [`Source`](#pydoc:lunatask.models.source.Source)
          to filter the output.

        Returns:
        * A list of [`Task`](#pydoc:lunatask.models.task.Task)s.
        """
        params = {}
        if source is not None:
            if source.source is not None:
                params["source"] = source.source
            if source.source_id is not None:
                params["source_id"] = source.source_id

        response = self._requests.get(
            f"{API_ENDPOINT}/tasks",
            headers=self.request_headers,
            timeout=self.api_timeout,
            params=params,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return [Task.from_dict(x) for x in response_json["tasks"]]

    def update_task(
        self: Self, task: Task, name: str | None = None, note: str | None = None
    ) -> Task:
        """Update a task.

        <https://lunatask.app/api/tasks-api/update>

        Arguments:
        * `task` - The [`Task`](#pydoc:lunatask.models.task.Task) to update.
        * `name` - The new name of the Task, if specified.
        * `note` - The new note for the Task, if specified.

        Returns:
        The updated [`Task`](#pydoc:lunatask.models.task.Task).
        """
        update = task.to_dict()
        if name is not None:
            update["name"] = name
        if note is not None:
            update["note"] = note

        response = self._requests.put(
            f"{API_ENDPOINT}/tasks/{task.id}",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=update,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return Task.from_dict(response_json["task"])

    ###########################################################################
    # Note APIs
    ###########################################################################

    def create_note(
        self: Self,
        notebook_id: UUID,
        name: str,
        content: str,
        date_on: datetime.datetime | None = None,
        source: Source | None = None,
    ) -> Note:
        """Create a new Note.

        Raises a RequestException with HTTPStatus.NO_CONTENT if a note with
        the same source already exists in the given notebook.

        <https://lunatask.app/api/notes-api/create>

        Arguments:
        * `notebook_id` - UUID of the Lunatask notebook ("Get Notebook ID"
          button).
        * `name` - Name of the note. *Technically* optional in the Lunatask API.
        * `content` - Markdown-formatted content of the note.
        * `date_on` -  Date assigned to the note.
        * `source` - Source of the note.

        Returns:
        The new [`Note`](#pydoc:lunatask.models.note.Note).
        """
        params = {
            "notebook_id": notebook_id,
            "name": name,
            "content": content,
        }
        if date_on:
            params["date_on"] = date_on.isoformat()
        if source:
            params["source"] = source.source
            if source.source_id:
                params["source_id"] = source.source_id

        response = self._requests.post(
            f"{API_ENDPOINT}/notes",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=params,
        )

        if response.status_code not in [HTTPStatus.CREATED, HTTPStatus.NO_CONTENT]:
            response.raise_for_status()

        if response.status_code == HTTPStatus.NO_CONTENT:
            raise self._requests.RequestException(response=response)

        response_json = response.json()
        return Note.from_dict(response_json["note"])

    ###########################################################################
    # Habit APIs
    ###########################################################################

    def track_habit(
        self: Self, habit: UUID, performed_on: datetime.datetime | None = None
    ) -> None:
        """Update the given habit, performed at the given date/time.

        <https://lunatask.app/api/habits-api/track-activity>

        Arguments:
        * `habit` - The habit's UUID from Lunatask ("Copy Habit ID" button).
        * `performed_on` - A `datetime` indicating when the habit was performed.
          If `None`, use the current time.
        """
        tracked_habit = {}
        if performed_on:
            tracked_habit["performed_on"] = performed_on.isoformat()
        else:
            tracked_habit["performed_on"] = datetime.datetime.now().astimezone()

        # This comes back as {"status": "OK"}, which we can ignore.
        response = self._requests.post(
            f"{API_ENDPOINT}/habits/{habit}/track",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=tracked_habit,
        )

        if response.status_code != HTTPStatus.CREATED:
            response.raise_for_status()

    ###########################################################################
    # People APIs
    ###########################################################################

    def create_person(
        self: Self,
        new_person: NewPerson,
        custom_fields: dict[str, str | datetime.datetime] | None = None,
    ) -> Person:
        """Create a new person.

        The `custom_fields` must exist (or have existed) on a Person in the
        app before you can create them with the API. The ones shown in the API
        documentation include:

        * `email`
        * `birthday`
        * `phone`

        The app lets you create:

        * Email
        * Phone Number
        * Social Profile URL
        * Link
        * Anniversary
        * Date
        * Text / Note (Markdown Enabled)

        Custom fields can be named anything when you create them.

        If you haven't previously created a custom field on a Peron in the app,
        it throws `RequestException` with `UNPROCESSABLE_CONTENT`.

        You don't need to keep the Person with the custom field, it's available
        forever.

        Throws `RequestException` if you're creating a Person with the same
        `source` and `source_id` as an existing Person. The exception's
        `response.status_code` will be `HTTPStatus.NO_CONTENT`.

        <https://lunatask.app/api/people-api/create-person>

        Arguments:
        * `new_person` - A [`NewPerson`](#pydoc:lunatask.models.people.NewPerson)
        used to create the `Person`.
        * `custom_fields` - An optional dictionary of custom field names and
        the data to assign to them. Read the notes above though.

        Returns:
        The newly created [`Person`](#pydoc:lunatask.models.people.Person).
        """
        # TODO: You can create a "first_name" custom field; what's it's "real"
        # name in the API? How do field names in general translate into the
        # custom field names used by the API?

        new_person_dict = new_person.to_dict()
        if custom_fields:
            for k in custom_fields:
                new_person_dict[k] = custom_fields[k]

        response = self._requests.post(
            f"{API_ENDPOINT}/people",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=new_person_dict,
        )

        if response.status_code not in [
            HTTPStatus.CREATED,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.UNPROCESSABLE_CONTENT,
        ]:
            response.raise_for_status()

        if response.status_code == HTTPStatus.NO_CONTENT:
            # Duplicate Source.
            raise self._requests.RequestException(response=response)

        if response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT:
            # Custom Fields not defined in the app.
            raise self._requests.RequestException(response=response)

        response_json = response.json()
        return Person.from_dict(response_json["person"])

    def delete_person(self: Self, person_id: UUID) -> Person:
        """Delete the specified Person.

        <https://lunatask.app/api/people-api/delete>

        Arguments:
        * `person_id` - The [`Person`](#pydoc:lunatask.models.people.Person)'s
          UUID.

        Returns:
        The deleted [`Person`](#pydoc:lunatask.models.people.Person).
        """
        response = self._requests.delete(
            f"{API_ENDPOINT}/people/{person_id}",
            headers=self.request_headers,
            timeout=self.api_timeout,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return Person.from_dict(response_json["person"])

    def get_people(self: Self, source: Source | None = None) -> list[Person]:
        """Get all people.

        If `source` is specified, the result is limited to people from that
        source (and with that `source_id` if specified), otherwise all people
        are returned.

        <https://lunatask.app/api/people-api/list>

        Arguments:
        * `source` - An optional [`Source`](#pydoc:lunatask.models.source.Source)
          to use as a filter.

        Returns:
        * A list of [`Person`](#pydoc:lunatask.models.person.Person)s.
        """
        params = {}
        if source is not None:
            params["source"] = source.source
            if source.source_id is not None:
                params["source_id"] = source.source_id

        response = self._requests.get(
            f"{API_ENDPOINT}/people",
            headers=self.request_headers,
            timeout=self.api_timeout,
            params=params,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return [Person.from_dict(x) for x in response_json["people"]]

    def get_person(self: Self, person_id: UUID) -> Person:
        """Get the specified Person.

        <https://lunatask.app/api/people-api/show>

        Arguments:
        * `person_id` - The [`Person`](#pydoc:lunatask.models.people.Person)'s
          UUID.

        Returns:
        The [`Person`](#pydoc:lunatask.models.people.Person).
        """
        response = self._requests.get(
            f"{API_ENDPOINT}/people/{person_id}",
            headers=self.request_headers,
            timeout=self.api_timeout,
        )

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        response_json = response.json()
        return Person.from_dict(response_json["person"])

    ###########################################################################
    # People Timeline Note APIs
    ###########################################################################

    def create_timeline_note(
        self: Self,
        person_id: UUID,
        date_on: datetime.datetime | None = None,
        content: str | None = None,
    ) -> TimelineNote:
        """Create a Person Timeline Note.

        <https://lunatask.app/api/person-timeline-notes-api/create>

        Arguments:
        * `person_id` - The [`Person`](#pydoc:lunatask.models.people.Person)'s
          UUID.
        * `date_on` - An optional `datetime` for this note.
        * `content` - The note's content. *Technically* optional.

        Returns:
        The newly created
        [TimelineNote](#pydoc:lunatask.models.timeline_note.TimelineNote).
        """
        params = {
            "person_id": str(person_id),
        }
        if date_on:
            params["date_on"] = date_on.isoformat()
        if content:
            params["content"] = content

        response = self._requests.post(
            f"{API_ENDPOINT}/person_timeline_notes",
            headers=self.request_headers,
            timeout=self.api_timeout,
            json=params,
        )

        if response.status_code != HTTPStatus.CREATED:
            response.raise_for_status()

        response_json = response.json()
        return TimelineNote.from_dict(response_json["person_timeline_note"])
