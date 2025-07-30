"""Configuration file object."""

import string
from dataclasses import dataclass, field
from typing import Annotated, Final, Self
from uuid import UUID

from dataclass_wizard import KeyPath, TOMLWizard

# Current API tokens are expected to be:
#
# - Todoist: 40 characters, hex
# - Lunatask: 600 characters, [A-Za-z0-9._]
#
# Lunatask's token seems to be split into three fields by the "." characters.
# Not sure about the encoding.
LUNATASK_API_TOKEN_LENGTH: Final[int] = 600
TODOIST_API_TOKEN_LENGTH: Final[int] = 40

LUNTASK_API_TOKEN_VALID: Final[str] = (
    ".-_" + string.ascii_uppercase + string.ascii_lowercase + string.digits
)
TODOIST_API_TOKEN_VALID: Final[str] = string.hexdigits

DEFAULT_UPCOMING_DAYS: Final[int] = 7

DEFAULT_PRIORITY_GLYPHS: Final[dict[str, str]] = {
    "p1": "⏫",
    "p2": "🔼",
    "p3": "⏩",
    "p4": "🔽",
}

DEFAULT_MARKDOWN_TEMPLATES: Final[dict[str, str]] = {
    "task-comments": "#### Comments\n\n{comment_list}\n",
    "task-comment-list": "> {comment}",
    "task-deadline": "Deadline: {deadline_date}",
    "task-due": "Due: {due_date}{recurring}{arbitrary}",
    "task-labels": "Labels: {label_list}",
    "task-label-list": "{favourite}{name} ({colour})",
    "task-parent": "* Parent task: {priority_glyph} {area} 🠖 {name}",
    "task-section": "**Section:** {name}",
    "task-subtasks": "#### Sub-tasks\n\n{subtask_list}\n",
    "task-subtask-list": "[] Sub-task: {priority_glyph} {area} 🠖 {name}",
}


class MissingPriorityError(KeyError):
    """The Priority mapping is missing a value."""


class TokenLengthError(ValueError):
    """The API token has an invalid length."""


class TokenInvalidCharacterError(ValueError):
    """The API token has invalid characters."""


@dataclass
class Config(TOMLWizard):
    """todoist2lunatask configuration.

    You *MUST* supply API tokens and a default area ID, everything else is
    optional. See the todoist2lunatask.config.template for examples and
    detailed docs.
    """

    # Required config settings:

    # API tokens
    lunatask_api_token: str
    todoist_api_token: str

    todoist_default_area: UUID

    # Optional config settings.

    # Task mapping
    todoist_project_map: dict[str, UUID] = field(default_factory=dict)

    todoist_task_source: Annotated[str, KeyPath("optional.todoist_task_source")] = (
        "Todoist"
    )
    todoist_upcoming_days: Annotated[int, KeyPath("optional.todoist_upcoming_days")] = 7
    todoist_label_reminder: Annotated[
        str, KeyPath("optional.todoist_label_reminder")
    ] = "Create Goals for Todoist Labels"
    todoist_recurring_reminder: Annotated[
        str, KeyPath("optional.todoist_recurring_reminder")
    ] = "Update recurring tasks"

    todoist_priority: dict[str, int] = field(
        default_factory=lambda: {"p1": 2, "p2": 1, "p3": 0, "p4": -1}
    )

    priority_glyph: dict[str, str] = field(
        default_factory=lambda: DEFAULT_PRIORITY_GLYPHS
    )

    markdown_templates: dict[str, str] = field(
        default_factory=lambda: DEFAULT_MARKDOWN_TEMPLATES
    )

    def __post_init__(self: Self) -> None:
        """Sanity check config."""
        # Check API tokens.
        if len(self.todoist_api_token) != TODOIST_API_TOKEN_LENGTH:
            msg = f"Todoist token should be {TODOIST_API_TOKEN_LENGTH}, not "
            f"{len(self.todoist_api_token)}"
            raise TokenLengthError(msg)

        if len(self.lunatask_api_token) != LUNATASK_API_TOKEN_LENGTH:
            msg = f"Lunatask token should be {LUNATASK_API_TOKEN_LENGTH}, not "
            f"{len(self.lunatask_api_token)}"
            raise TokenLengthError(msg)

        for c in self.todoist_api_token:
            if c not in TODOIST_API_TOKEN_VALID:
                msg = f"Invalid Todoist token character: {c}"
                raise TokenInvalidCharacterError(msg)

        for c in self.lunatask_api_token:
            if c not in LUNTASK_API_TOKEN_VALID:
                msg = f"Invalid Lunatask token character: {c}"
                raise TokenInvalidCharacterError(msg)

        # Check priority map.
        for k in ["p1", "p2", "p3", "p4"]:
            if k not in self.todoist_priority:
                raise MissingPriorityError(k)

        # Sanity for Markdown templates.
        for k in DEFAULT_PRIORITY_GLYPHS:
            if k not in self.priority_glyph:
                self.priority_glyph[k] = DEFAULT_PRIORITY_GLYPHS[k]

        for k in DEFAULT_MARKDOWN_TEMPLATES:
            if k not in self.markdown_templates:
                self.markdown_templates[k] = DEFAULT_MARKDOWN_TEMPLATES[k]
