"""Lunatask Note objects.

<https://lunatask.app/api/notes-api/entity>
"""

import datetime
from dataclasses import dataclass
from uuid import UUID

from dataclass_wizard import DumpMixin, JSONPyWizard, JSONWizard, LoadMixin
from dataclass_wizard.enums import DateTimeTo

from lunatask.models.source import Source


@dataclass
class Note(JSONPyWizard, LoadMixin, DumpMixin):
    """A Lunatask Note.

    Required Fields:
    * `created_at: datetime.datetime`
    * `id: UUID`
    * `notebook_id: UUID`
    * `sources: list[Source]`
    * `updated_at: datetime.datetime`

    Optional Fields:
    * `date_on: datetime.datetime | None` Default: `None`
    * `deleted_at: datetime.datetime | None` Default: `None`
    * `pinned: bool` Default: `False`

    Undocumented Fields:
    * `pinned: bool` - Whether the `Note` is "pinned" in the app.
    """

    class _(JSONWizard.Meta):  # noqa: N801
        marshall_date_time_as = DateTimeTo.ISO_FORMAT
        skip_defaults = True

    created_at: datetime.datetime
    id: UUID
    notebook_id: UUID
    sources: list[Source]
    updated_at: datetime.datetime

    date_on: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None

    pinned: bool = False
