"""Sample Notes for unit tests.

id: UUID
notebook_id: UUID
sources: Sources
pinned: bool
created_at: datetime.datetime
updated_at: datetime.datetime

date_on: datetime.datetime | None = None
deleted_at: datetime.datetime | None = None
"""

import datetime
import uuid
from typing import Any, Final

TEST_DATE: Final[datetime.datetime] = datetime.datetime.fromisoformat("2025-04-27")
TEST_UUID_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "id")
TEST_UUID_NOTEBOOK_ID: Final[uuid.UUID] = uuid.uuid3(uuid.NAMESPACE_URL, "notebook_id")

dict_note_full: Final[dict[str, Any]] = {
    "id": str(TEST_UUID_ID),
    "notebook_id": str(TEST_UUID_NOTEBOOK_ID),
    "date_on": TEST_DATE,
    "sources": [{"source": "test source", "source_id": "0"}],
    "pinned": False,
    "created_at": TEST_DATE,
    "updated_at": TEST_DATE,
    "deleted_at": TEST_DATE,
}

dict_note_no_optional: Final[dict[str, Any]] = {
    k: dict_note_full[k]
    for k in dict_note_full
    if k not in ["date_on", "deleted_at", "sources"]
}
dict_note_no_optional["sources"] = []
