"""Test the Note data classes.

Note:
    id: UUID
    notebook_id: UUID
    sources: Sources
    pinned: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    date_on: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
"""

# ruff: noqa: D103, S101

import pytest
from dataclass_wizard.errors import MissingFields

from lunatask.models import note
from tests.data.sample_note import (
    TEST_DATE,
    TEST_UUID_ID,
    TEST_UUID_NOTEBOOK_ID,
    dict_note_full,
    dict_note_no_optional,
)


def test_note_from_dict() -> None:
    # Full
    test_note = note.Note.from_dict(dict_note_full)
    assert test_note.id == TEST_UUID_ID
    assert test_note.notebook_id == TEST_UUID_NOTEBOOK_ID
    assert test_note.sources[0].source == "test source"
    assert test_note.sources[0].source_id == "0"
    with pytest.raises(IndexError):
        _ = test_note.sources[1]
    assert not test_note.pinned
    assert test_note.created_at == TEST_DATE
    assert test_note.updated_at == TEST_DATE
    assert test_note.date_on == TEST_DATE
    assert test_note.deleted_at == TEST_DATE


def test_note_from_dict_partial() -> None:
    # No optional
    test_note = note.Note.from_dict(dict_note_no_optional)
    assert test_note.id == TEST_UUID_ID
    assert test_note.notebook_id == TEST_UUID_NOTEBOOK_ID
    assert test_note.sources == []
    with pytest.raises(IndexError):
        _ = test_note.sources[0]
    assert not test_note.pinned
    assert test_note.created_at == TEST_DATE
    assert test_note.updated_at == TEST_DATE

    assert test_note.date_on is None
    assert test_note.deleted_at is None


def test_note_empty() -> None:
    with pytest.raises(MissingFields):
        _ = note.Note.from_dict({})


def test_note_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = note.Note.from_json("{}")


def test_note_invalid() -> None:
    invalid_dict = {k: dict_note_full[k] for k in dict_note_full}
    invalid_dict["id"] = "Hello, world"
    with pytest.raises(ValueError):  # noqa: PT011
        _ = note.Note.from_dict(invalid_dict)
