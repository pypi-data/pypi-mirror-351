"""Lunatask Task objects.

Task enums: <https://lunatask.app/api/tasks-api/entity>
"""

import datetime
from dataclasses import dataclass
from enum import IntEnum, StrEnum, unique
from uuid import UUID

from dataclass_wizard import JSONPyWizard, JSONWizard
from dataclass_wizard.enums import DateTimeTo

from lunatask.models.source import Source


@unique
class Status(StrEnum):
    """Task status values."""

    COMPLETED = "completed"
    LATER = "later"
    NEXT = "next"
    STARTED = "started"
    WAITING = "waiting"


@unique
class Priority(IntEnum):
    """Task priority values."""

    HIGHEST = 2
    HIGH = 1
    NORMAL = 0  # Default
    LOW = -1
    LOWEST = -2


@unique
class Motivation(StrEnum):
    """Task motivation values."""

    MUST = "must"
    SHOULD = "should"
    UNKNOWN = "unknown"  # Default
    WANT = "want"


@unique
class Eisenhower(IntEnum):
    """Task Eisenhower values."""

    URGENT_IMPORTANT = 1
    URGENT_NOT_IMPORTANT = 2
    NOT_URGENT_IMPORTANT = 3
    NOT_URGENT_NOT_IMPORTANT = 4
    UNCATEGORIZED = 0


@dataclass
class NewTask(JSONPyWizard):
    """A new Task, about to be added to Lunatask.

    Required Fields:
    * `area_id: UUID` - UUID for the Area of Life where this Task will be
      created.

    Optional Fields:
    * `completed_at: datetime | None` - When the Task was completed. Default:
      `None`
    * `eisenhower: Eisenhower` Default: `UNCATEGORIZED`
    * `estimate: int | None` - Estimated amount of time, in minutes, to finish
      this task. Default: `None` ("unknown")
    * `goal_id: UUID` - UUID of the task's Goal.
    * `motivation: Motivation` - Task motivation. Default: `UNKNOWN`
    * `name: str | None` - Task name, no Markdown support. *Technically*
      optional. Default: `None`
    * `note: str | None` - Task notes, with Markdown support. Default: `None`
    * `priority: Priority` - Task priority. Default: `NORMAL`
    * `scheduled_on: datetime | None` - When this task was created. Defaults to
      now, but optional if you set it to `None`.
    * `source: str` - The source of this task. Default: `None`
    * `source_id: str | None` - A source ID for this task. Default: `None`
    * `status` - Task status. Default: `LATER`
    """

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    area_id: UUID

    completed_at: datetime.datetime | None = None
    eisenhower: Eisenhower = Eisenhower.UNCATEGORIZED
    estimate: int | None = None  # Estimate in minutes
    goal_id: UUID | None = None
    motivation: Motivation = Motivation.UNKNOWN
    name: str | None = None  # Name of the task, no Markdown support.
    note: str | None = None  # Task notes; Markdown supported.
    priority: Priority | None = None
    scheduled_on: datetime.datetime | None = None
    source: str | None = None
    source_id: str | None = None
    status: Status = Status.LATER


@dataclass
class Task(JSONPyWizard):
    """A Lunatask task.

    https://lunatask.app/api/tasks-api/entity

    Task data available to the API is entirely metadata; the task name and
    notes (for example) are encrypted and only visible in the Lunatask app.

    Could we get the encrypted data via future API calls and decrypt
    them ourselves?

    Required Fields:
    * `area_id: UUID` - The Area of Life this Task belongs to.
    * `created_at: datetime` - When the Task was created.
    * `eisenhower: Eisenhower` - Eisenhower classification.
    * `id: UUID` - The Task's ID.
    * `motivation: Motivation` - How motivating this Task is.
    * `sources: list[Source]` - List of
      [`Source`](#pydoc:lunatask.models.source.Source)s of this Task.
    * `status: Status` - Status of the Task.
    * `updated_at: datetime` - When the Task was last updated.

    Optional Fields:
    * `completed_at: datetime | None` - When the Task was completed. Default:
      `None`
    * `estimate: int | None` Estimated time (in minutes) to complete the Task.
      Default: `None`
    * `goal_id: UUID | None` - The Task's Goal, if any. Default: `None`
    * `previous_status: Status | None` - The Task's previous `status`. Default:
      `None`
    * `priority: Priority | None` - The Task's priority.  Default: `None`
    * `progress: float | None` - Progress on the Task, in percent. Default:
      `None`
    * `scheduled_on: datetime | None` - The Task's scheduled date. Default:
      `None`

    Undocumented Fields:
    * `deleted_at: datetime | None` - When the task was deleted. Default: `None`
    """

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    area_id: UUID
    created_at: datetime.datetime
    eisenhower: Eisenhower
    id: UUID
    motivation: Motivation
    sources: list[Source]
    status: Status
    updated_at: datetime.datetime

    completed_at: datetime.datetime | None = None
    estimate: int | None = None
    goal_id: UUID | None = None
    previous_status: Status | None = None
    priority: Priority | None = None
    progress: float | None = None
    scheduled_on: datetime.datetime | None = None

    deleted_at: datetime.datetime | None = None
