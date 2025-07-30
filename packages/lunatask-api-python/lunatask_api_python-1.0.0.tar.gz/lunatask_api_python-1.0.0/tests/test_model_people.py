"""Test the data classes.

people.py models:

NewPerson:
    first_name: str
    last_name: str
    relationship_strength: Relationship = Relationship.CASUAL_FRIENDS

    source: str | None = None
    source_id: str | None = None

Person:
    id: UUID
    relationship_strength: Relationship = Relationship.CASUAL_FRIENDS
    relationship_direction: RelationshipDirection = RelationshipDirection.OKAY
    sources: Sources = field(default_factory=Sources)
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

    deleted_at: datetime.datetime | None = None
    agreed_reconnect_on: datetime.datetime | None = None
    last_reconnect_on: datetime.datetime | None = None
    next_reconnect_on: datetime.datetime | None = None
"""

# ruff: noqa: D103, S101

import pytest
from dataclass_wizard.errors import MissingFields

from lunatask.models import people
from tests.data.sample_people import (
    TEST_DATE,
    TEST_UUID_ID,
    dict_newperson_full,
    dict_newperson_no_optional,
    dict_person_full,
    dict_person_no_optional,
)


def test_newperson_from_dict() -> None:
    test_newperson = people.NewPerson.from_dict(dict_newperson_full)
    assert test_newperson.first_name == "Chris"
    assert test_newperson.last_name == "Herborth"
    assert test_newperson.relationship_strength == people.Relationship.FAMILY
    assert test_newperson.source == "unittest"
    assert test_newperson.source_id == "1"


def test_newperson_from_dict_partial() -> None:
    test_newperson = people.NewPerson.from_dict(dict_newperson_no_optional)
    assert test_newperson.first_name == "Chris"
    assert test_newperson.last_name == "Herborth"
    assert test_newperson.relationship_strength == people.Relationship.FAMILY
    assert test_newperson.source is None
    assert test_newperson.source_id is None


def test_newperson_empty() -> None:
    with pytest.raises(MissingFields):
        _ = people.NewPerson.from_dict({})


def test_newperson_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = people.NewPerson.from_json("{}")


def test_newperson_invalid() -> None:
    invalid_dict = {k: dict_newperson_full[k] for k in dict_newperson_full}
    invalid_dict["relationship_strength"] = "Hello, world"
    with pytest.raises(ValueError):  # noqa: PT011
        _ = people.NewPerson.from_dict(invalid_dict)


def test_person_from_dict() -> None:
    test_person = people.Person.from_dict(dict_person_full)
    assert test_person.id == TEST_UUID_ID
    assert test_person.relationship_strength == people.Relationship.FAMILY
    assert test_person.relationship_direction == people.RelationshipDirection.OKAY
    assert test_person.sources[0].source == "test source"
    assert test_person.sources[0].source_id == "0"
    with pytest.raises(IndexError):
        _ = test_person.sources[1]
    assert test_person.created_at == TEST_DATE
    assert test_person.updated_at == TEST_DATE
    assert test_person.deleted_at == TEST_DATE
    assert test_person.agreed_reconnect_on == TEST_DATE
    assert test_person.last_reconnect_on == TEST_DATE
    assert test_person.next_reconnect_on == TEST_DATE


def test_person_from_dict_partial() -> None:
    test_person = people.Person.from_dict(dict_person_no_optional)
    assert test_person.id == TEST_UUID_ID
    assert test_person.relationship_strength == people.Relationship.FAMILY
    assert test_person.relationship_direction == people.RelationshipDirection.OKAY
    assert test_person.sources == []
    with pytest.raises(IndexError):
        _ = test_person.sources[0]
    assert test_person.created_at == TEST_DATE
    assert test_person.updated_at == TEST_DATE
    assert test_person.deleted_at is None
    assert test_person.agreed_reconnect_on is None
    assert test_person.last_reconnect_on is None
    assert test_person.next_reconnect_on is None


def test_person_empty() -> None:
    with pytest.raises(MissingFields):
        _ = people.Person.from_dict({})


def test_person_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = people.Person.from_json("{}")


def test_person_invalid() -> None:
    invalid_dict = {k: dict_person_full[k] for k in dict_person_full}
    invalid_dict["id"] = "Hello, world"
    with pytest.raises(ValueError):  # noqa: PT011
        _ = people.Person.from_dict(invalid_dict)
