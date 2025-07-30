"""Sample TimelineNote for unit tests.

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

import datetime
import uuid
from typing import Any, Final

DEFAULT_DATE: Final[datetime.datetime] = datetime.datetime.fromisoformat(
    "1970-01-01T00:00:00.000Z"
)
TEST_CONTENT: Final[str] = "Hello, world."
TEST_DATE: Final[datetime.datetime] = datetime.datetime.fromisoformat("2025-04-29")
TEST_UUID_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "id")
TEST_UUID_PERSON_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "person_id")

dict_timeline_note_full: Final[dict[str, Any]] = {
    "id": str(TEST_UUID_ID),
    "person_id": str(TEST_UUID_PERSON_ID),
    "date_on": TEST_DATE,
    "created_at": TEST_DATE,
    "updated_at": TEST_DATE,
    "deleted_at": TEST_DATE,
    "content": TEST_CONTENT,
}

dict_timeline_note_no_optional: Final[dict[str, Any]] = {
    k: dict_timeline_note_full[k]
    for k in dict_timeline_note_full
    if k not in ["content", "date_on"]
}
