"""Test the data classes.

task.py models:

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
    source: Source | None = None

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

# ruff: noqa: D103, S101

import pytest
from dataclass_wizard.errors import MissingFields

from lunatask.models import task
from tests.data.sample_task import (
    TEST_DATE,
    TEST_UUID_AREA_ID,
    TEST_UUID_GOAL_ID,
    TEST_UUID_ID,
    dict_newtask_full,
    dict_newtask_no_optional,
    dict_task_full,
    dict_task_no_optional,
)


def test_newtask_from_dict() -> None:
    test_newtask = task.NewTask.from_dict(dict_newtask_full)
    assert test_newtask.area_id == TEST_UUID_AREA_ID
    assert test_newtask.goal_id == TEST_UUID_GOAL_ID
    assert test_newtask.name == "Task Name"
    assert test_newtask.note == "Task note."
    assert test_newtask.status == task.Status.WAITING
    assert test_newtask.motivation == task.Motivation.SHOULD
    assert test_newtask.eisenhower == task.Eisenhower.NOT_URGENT_NOT_IMPORTANT
    assert test_newtask.priority == task.Priority.LOW
    assert test_newtask.scheduled_on == TEST_DATE
    assert test_newtask.completed_at == TEST_DATE
    assert test_newtask.source == "A source"
    assert test_newtask.source_id == "1"


def test_newtask_from_dict_partial() -> None:
    test_newtask = task.NewTask.from_dict(dict_newtask_no_optional)
    assert test_newtask.area_id == TEST_UUID_AREA_ID
    assert test_newtask.goal_id is None
    assert test_newtask.name is None
    assert test_newtask.note is None
    assert test_newtask.status == task.Status.WAITING
    assert test_newtask.motivation == task.Motivation.SHOULD
    assert test_newtask.eisenhower == task.Eisenhower.NOT_URGENT_NOT_IMPORTANT
    assert test_newtask.priority == task.Priority.LOW
    assert test_newtask.scheduled_on is None
    assert test_newtask.completed_at is None
    assert test_newtask.source is None
    assert test_newtask.source_id is None


def test_newtask_empty() -> None:
    with pytest.raises(MissingFields):
        _ = task.NewTask.from_dict({})


def test_newtask_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = task.NewTask.from_json("{}")


def test_task_from_dict() -> None:
    test_task = task.Task.from_dict(dict_task_full)
    assert test_task.id == TEST_UUID_ID
    assert test_task.area_id == TEST_UUID_AREA_ID
    assert test_task.goal_id == TEST_UUID_GOAL_ID
    assert test_task.status == task.Status.WAITING
    assert test_task.priority == task.Priority.LOW
    assert test_task.motivation == task.Motivation.SHOULD
    assert test_task.eisenhower == task.Eisenhower.NOT_URGENT_NOT_IMPORTANT
    assert test_task.sources[0].source == "A source"
    assert test_task.sources[0].source_id == "1"
    with pytest.raises(IndexError):
        _ = test_task.sources[1]
    assert test_task.created_at == TEST_DATE
    assert test_task.updated_at == TEST_DATE
    assert test_task.previous_status == task.Status.WAITING
    assert test_task.estimate == 5  # noqa: PLR2004
    assert test_task.progress == 0.0
    assert test_task.scheduled_on == TEST_DATE
    assert test_task.completed_at == TEST_DATE
    assert test_task.deleted_at == TEST_DATE


def test_task_from_dict_partial() -> None:
    test_task = task.Task.from_dict(dict_task_no_optional)
    assert test_task.id == TEST_UUID_ID
    assert test_task.area_id == TEST_UUID_AREA_ID
    assert test_task.goal_id is None
    assert test_task.status == task.Status.WAITING
    assert test_task.priority == task.Priority.LOW
    assert test_task.motivation == task.Motivation.SHOULD
    assert test_task.eisenhower == task.Eisenhower.NOT_URGENT_NOT_IMPORTANT
    assert test_task.sources == []
    with pytest.raises(IndexError):
        _ = test_task.sources[0]
    assert test_task.created_at == TEST_DATE
    assert test_task.updated_at == TEST_DATE
    assert test_task.previous_status is None
    assert test_task.estimate is None
    assert test_task.progress is None
    assert test_task.scheduled_on is None
    assert test_task.completed_at is None
    assert test_task.deleted_at is None


def test_task_empty() -> None:
    with pytest.raises(MissingFields):
        _ = task.Task.from_dict({})


def test_task_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = task.Task.from_json("{}")
