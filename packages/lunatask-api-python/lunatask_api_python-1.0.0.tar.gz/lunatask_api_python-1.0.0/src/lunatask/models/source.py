"""Lunatask Source objects."""

from dataclasses import dataclass

from dataclass_wizard import JSONPyWizard


class MissingSourceIdError(Exception):
    """When creating a Task with a Source, you must include the source_id."""


@dataclass
class Source(JSONPyWizard):
    """The source of a task, note, etc.

    Optional information about where an item came from, indicating an import
    tool or other application.

    Required Fields:
    * `source: str` - An identifier for the source ("GitHub", "Todoist", *etc.*).

    Optional Fields:
    * `source_id: str` - An ID value from the original source (GitHub Issue ID,
      *etc.*).
    """

    source: str

    source_id: str | None = None
