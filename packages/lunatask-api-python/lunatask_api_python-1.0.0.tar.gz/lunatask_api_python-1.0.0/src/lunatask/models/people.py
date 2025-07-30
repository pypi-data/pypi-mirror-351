"""Lunatask People objects.

<https://lunatask.app/api/people-api/list>
"""

import datetime
from dataclasses import dataclass, field
from enum import StrEnum, auto, unique
from uuid import UUID

from dataclass_wizard import JSONPyWizard, JSONWizard
from dataclass_wizard.enums import DateTimeTo

from lunatask.models.source import Source


# People enums
@unique
class Relationship(StrEnum):
    """Person relationship values."""

    ACQUAINTANCES = auto()
    ALMOST_STRANGERS = "almost-strangers"
    BUSINESS_CONTACTS = "business-contacts"
    CASUAL_FRIENDS = "casual-friends"
    CLOSE_FRIENDS = "close-friends"
    FAMILY = auto()
    INTIMATE_FRIENDS = "intimate-friends"


@unique
class RelationshipDirection(StrEnum):
    """Relationship status.

    This enum is undocumented in the API.
    """

    IMPROVE = "improve"
    OKAY = "okay"


@dataclass
class NewPerson(JSONPyWizard):
    """Used to create a new Person in Lunatask.

    Build one of these for the `create_person()` method.

    Required Fields:
    * `first_name: str`
    * `last_name: str`

    Optional Fields:
    * `relationship_strength: Relationship` Default: `CASUAL_FRIENDS`
    * `source_id: str | None` Default: `None`
    * `source: str | None` Default: `None`
    """

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    first_name: str
    last_name: str

    relationship_strength: Relationship = Relationship.CASUAL_FRIENDS
    source_id: str | None = None
    source: str | None = None


@dataclass
class Person(JSONPyWizard):
    """A Lunatask Person object.

    Required Fields:
    * `id: UUID`

    Optional Fields:
    * `relationship_direction: RelationshipDirection | None` Default: `OKAY`
    * relationship_strength: Relationship` Default: `CASUAL_FRIENDS`
    * `sources: list[Source]` Default: `[]`
    * `created_at: datetime.datetime` Default: "1970-01-01T00:00:00.000Z"
    * `updated_at: datetime.datetime` Default: "1970-01-01T00:00:00.000Z"

    Undocumented Fields:
    * `deleted_at: datetime` - When this record was deleted.
    * `agreed_reconnect_on: datetime` - When you're going to reconnect.
    * `last_reconnect_on: datetime` - Last time you reconnected.
    * `next_reconnect_on: datetime` - Next time you'll reconnect.
    * `relationship_direction: RelationshipDirection` - How's your relationship?
    """

    # TODO: <https://codeberg.org/Taffer/todoist2lunatask/issues/3>
    # How to handle custom fields?

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    id: UUID

    relationship_direction: RelationshipDirection | None = RelationshipDirection.OKAY
    relationship_strength: Relationship = Relationship.CASUAL_FRIENDS
    sources: list[Source] = field(default_factory=list)
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

    agreed_reconnect_on: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
    last_reconnect_on: datetime.datetime | None = None
    next_reconnect_on: datetime.datetime | None = None
