"""Sample NewPerson and Person for unit tests.

NewPerson:
    first_name: str
    last_name: str
    relationship_strength: Relationship = Relationship.CASUAL_FRIENDS

    source: str | None = None
    source_id: str | None = None
    email: str | None = None
    birthday: datetime.datetime | None = None
    phone: str | None = None

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

import datetime
import uuid
from typing import Any, Final

from lunatask.models.people import Relationship, RelationshipDirection

TEST_DATE: Final[datetime.datetime] = datetime.datetime.fromisoformat("2025-01-01")
TEST_UUID_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "id")

dict_newperson_full: Final[dict[str, Any]] = {
    "first_name": "Chris",
    "last_name": "Herborth",
    "relationship_strength": Relationship.FAMILY,
    "source": "unittest",
    "source_id": "1",
}

dict_newperson_no_optional: Final[dict[str, Any]] = {
    k: dict_newperson_full[k]
    for k in dict_newperson_full
    if k
    not in [
        "source_id",
        "source",
    ]
}

dict_person_full: Final[dict[str, Any]] = {
    "id": str(uuid.uuid3(uuid.NAMESPACE_URL, "id")),
    "relationship_strength": Relationship.FAMILY,
    "relationship_direction": RelationshipDirection.OKAY,
    "sources": [{"source": "test source", "source_id": "0"}],
    "created_at": TEST_DATE,
    "updated_at": TEST_DATE,
    "deleted_at": TEST_DATE,
    "agreed_reconnect_on": TEST_DATE,
    "last_reconnect_on": TEST_DATE,
    "next_reconnect_on": TEST_DATE,
}

dict_person_no_optional: Final[dict[str, Any]] = {
    k: dict_person_full[k]
    for k in dict_person_full
    if k
    not in [
        "agreed_reconnect_on",
        "deleted_at",
        "last_reconnect_on",
        "next_reconnect_on",
        "sources",
    ]
}
dict_person_no_optional["sources"] = []
