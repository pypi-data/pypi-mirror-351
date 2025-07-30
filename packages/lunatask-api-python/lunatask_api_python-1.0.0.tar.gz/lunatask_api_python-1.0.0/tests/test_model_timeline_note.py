"""Test the data classes.

timeline_note.py models:

TimelineNote:
    id: UUID
    person_id: UUID
    date_on: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    deleted_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    content: str | None = None
"""

# ruff: noqa: D103, S101

import pytest
from dataclass_wizard.errors import MissingFields

from lunatask.models import timeline_note
from tests.data.sample_timeline_note import (
    DEFAULT_DATE,
    TEST_CONTENT,
    TEST_DATE,
    TEST_UUID_ID,
    TEST_UUID_PERSON_ID,
    dict_timeline_note_full,
    dict_timeline_note_no_optional,
)


def test_timeline_note_from_dict() -> None:
    test_timeline_note = timeline_note.TimelineNote.from_dict(dict_timeline_note_full)
    assert test_timeline_note.id == TEST_UUID_ID
    assert test_timeline_note.person_id == TEST_UUID_PERSON_ID
    assert test_timeline_note.date_on == TEST_DATE
    assert test_timeline_note.created_at == TEST_DATE
    assert test_timeline_note.updated_at == TEST_DATE
    assert test_timeline_note.deleted_at == TEST_DATE
    assert test_timeline_note.content == TEST_CONTENT


def test_timeline_note_from_dict_partial() -> None:
    test_timeline_note = timeline_note.TimelineNote.from_dict(
        dict_timeline_note_no_optional
    )
    assert test_timeline_note.id == TEST_UUID_ID
    assert test_timeline_note.person_id == TEST_UUID_PERSON_ID
    assert test_timeline_note.date_on == DEFAULT_DATE
    assert test_timeline_note.created_at == TEST_DATE
    assert test_timeline_note.updated_at == TEST_DATE
    assert test_timeline_note.deleted_at == TEST_DATE
    assert test_timeline_note.content is None


def test_timeline_note_empty() -> None:
    with pytest.raises(MissingFields):
        _ = timeline_note.TimelineNote.from_dict({})


def test_timeline_note_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = timeline_note.TimelineNote.from_json("{}")


def test_timeline_note_invalid() -> None:
    invalid_dict = {k: dict_timeline_note_full[k] for k in dict_timeline_note_full}
    invalid_dict["id"] = "Hello, world"
    with pytest.raises(ValueError):  # noqa: PT011
        _ = timeline_note.TimelineNote.from_dict(invalid_dict)
