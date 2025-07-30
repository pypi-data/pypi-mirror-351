"""Sample Tasks for unit tests.

NewTask:
    area_id: UUID
    goal_id: UUID | None
    name: str | None  # Name of the task, no Markdown support.
    note: str | None  # Task notes; Markdown supported.
    status: Status = Status.LATER
    motivation: Motivation = Motivation.UNKNOWN
    eisenhower: Eisenhower = Eisenhower.UNCATEGORIZED
    estimate: int | None = None  # Estimate in minutes
    priority: Priority = Priority.NORMAL
    scheduled_on: datetime.datetime | None = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    completed_at: datetime.datetime | None = None  # ISO 8601 format
    source: str | None = None
    source_id: str | None = None

Task:
    id: UUID
    area_id: UUID
    goal_id: UUID | None
    status: Status
    priority: Priority
    motivation: Motivation
    eisenhower: Eisenhower
    sources: list[Source]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    previous_status: Status | None
    estimate: int | None
    progress: float | None
    scheduled_on: datetime.datetime | None
    completed_at: datetime.datetime | None
    deleted_at: datetime.datetime | None
"""

import datetime
import uuid
from typing import Any, Final

from lunatask.models.task import Eisenhower, Motivation, Priority, Status

TEST_DATE: Final[datetime.datetime] = datetime.datetime.fromisoformat("2025-04-30")
TEST_UUID_AREA_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "area_id")
TEST_UUID_GOAL_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "goal_id")
TEST_UUID_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "id")

dict_newtask_full: Final[dict[str, Any]] = {
    "area_id": str(TEST_UUID_AREA_ID),
    "goal_id": str(TEST_UUID_GOAL_ID),
    "name": "Task Name",
    "note": "Task note.",
    "status": Status.WAITING,
    "motivation": Motivation.SHOULD,
    "eisenhower": Eisenhower.NOT_URGENT_NOT_IMPORTANT,
    "priority": Priority.LOW,
    "scheduled_on": TEST_DATE,
    "completed_at": TEST_DATE,
    "source": "A source",
    "source_id": "1",
}

dict_newtask_no_optional: Final[dict[str, Any]] = {
    k: dict_newtask_full[k]
    for k in dict_newtask_full
    if k
    not in [
        "completed_at",
        "estimate",
        "goal_id",
        "name",
        "note",
        "scheduled_on",
        "source",
        "source_id",
    ]
}

dict_task_full: Final[dict[str, Any]] = {
    "id": str(TEST_UUID_ID),
    "area_id": str(TEST_UUID_AREA_ID),
    "goal_id": str(TEST_UUID_GOAL_ID),
    "status": Status.WAITING,
    "priority": Priority.LOW,
    "motivation": Motivation.SHOULD,
    "eisenhower": Eisenhower.NOT_URGENT_NOT_IMPORTANT,
    "sources": [{"source": "A source", "source_id": "1"}],
    "created_at": TEST_DATE,
    "updated_at": TEST_DATE,
    "previous_status": Status.WAITING,
    "estimate": 5,
    "progress": 0.0,
    "scheduled_on": TEST_DATE,
    "completed_at": TEST_DATE,
    "deleted_at": TEST_DATE,
}

dict_task_no_optional: Final[dict[str, Any]] = {
    k: dict_task_full[k]
    for k in dict_task_full
    if k
    not in [
        "completed_at",
        "deleted_at",
        "estimate",
        "goal_id",
        "previous_status",
        "progress",
        "scheduled_on",
        "sources",
    ]
}
dict_task_no_optional["sources"] = []
