"""Lunatask Person Timeline Note objects.

These are notes you attach to people to document your interactions with them.

<https://lunatask.app/api/person-timeline-notes-api/create>
"""

import datetime
from dataclasses import dataclass, field
from uuid import UUID

from dataclass_wizard import JSONPyWizard, JSONWizard
from dataclass_wizard.enums import DateTimeTo


@dataclass
class TimelineNote(JSONPyWizard):
    """A Lunatask Person Timeline Note object.

    Required Fields:
    * `id: UUID` - The ID of this timeline note.

    Optional Fields:
    * `created_at: datetime` - When this note was created. Defaults to the
      UNIX epoch.
    * `date_on: datetime` - When this interaction happened. Defaults to the
      UNIX epoch.
    * `updated_at: datetime` When this note was updated. Defaults to the
      UNIX epoch.

    Undocumented Fields:
    * `content: str` - Encrypted/encoded content of the note. Default: `None`
    * `deleted_at: datetime | None` - When this note was deleted. Default:
      `None`
    * `person_id: UUID` - The ID of the Person this note is attached to.
      Default: `None`
    """

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    id: UUID

    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    # TODO: Is `date_on` YYYY-MM-DD only, or is a time component just ignored?
    date_on: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.fromisoformat(
            "1970-01-01T00:00:00.000Z"
        )
    )

    content: str | None = None
    deleted_at: datetime.datetime | None = None
    person_id: UUID | None = None
