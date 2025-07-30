"""Import Todoist Tasks into Lunatask."""

import datetime
import os
import uuid
from typing import Final, Self, cast

from requests import HTTPError, RequestException
from todoist_api_python import models as TodoistModels  # noqa: N812
from todoist_api_python.api import TodoistAPI

from config import Config
from lunatask.api import LunataskAPI
from lunatask.models.task import Eisenhower, Motivation, NewTask, Priority, Status

# Number of minutes in a day, roughly.
DAY_MINUTES: Final[int] = 24 * 60

# Todoist priority value to representation.
PRIORITY_VALUE: Final[dict[int, str]] = {
    4: "p1",
    3: "p2",
    2: "p3",
    1: "p4",
}


class TodoistImporter:
    """Import Todoist Tasks into Lunatask.

    Things that end up in the Notes section:

    - comments
    - creation date
    - deadline
    - labels
    - recurrence info
    - section
    - sub-tasks
    - url

    Things that create additional tasks:

    - labels for the tasks that had them, and the areas they went
    into; create a new task in each area listing the tasks that had labels
    - tasks that were recurring and the areas they went into;
    create a new task in each area listing the tasks that were recurring,
    and a link to the instructions in Lunatask
    """

    config: Config

    luntask_api: LunataskAPI
    todoist_api: TodoistAPI

    # Data from Todoist. Not populated until you call import_tasks().
    labels: list[TodoistModels.Label]
    project_sections: dict[str, list[TodoistModels.Section]]
    projects: list[TodoistModels.Project]
    sections: list[TodoistModels.Section]
    task_comments: dict[str, list[TodoistModels.Comment]]
    tasks: list[TodoistModels.Task]

    # name -> thing lookups for Todoist data. Not populated until you call
    # import_tasks().
    label_map: dict[str, TodoistModels.Label]

    # ID -> thing lookups for Todoist data. Not populated until you call
    # import_tasks().
    project_map: dict[str, TodoistModels.Project]
    section_map: dict[str, TodoistModels.Section]
    task_map: dict[str, TodoistModels.Task]

    # These tasks had Labels. We collect them to create a new Lunatask Task to
    # remind you to create suitable Goals for them after the import. Not
    # populated until you call import_tasks().
    labelled_tasks: dict[uuid.UUID, list[TodoistModels.Task]]

    # These tasks are recurring, which requires additional setup in Lunatask.
    # Not populated until you call import_tasks().
    recurring_tasks: dict[uuid.UUID, list[TodoistModels.Task]]

    # Task IDs that have sub-tasks, and their sub-tasks. Not populated until
    # you call import_tasks().
    subtasks: dict[str, list[TodoistModels.Task]]

    def __init__(self: Self, config: Config) -> None:
        """Create the importer."""
        self.config = config

        # Defaults to PyRight doesn't think these are None.
        self.labels = []
        self.projects = []
        self.sections = []
        self.task_comments = {}
        self.tasks = []

        self.label_map = {}
        self.project_map = {}
        self.section_map = {}
        self.task_map = {}

        self.labelled_tasks = {}
        self.recurring_tasks = {}
        self.subtasks = {}

        try:
            self.todoist_api = TodoistAPI(self.config.todoist_api_token)
        except (HTTPError, RequestException) as ex:
            print(f"Unable to connect to Todoist API: {ex}")
            raise SystemExit(os.EX_IOERR) from ex

        try:
            self.luntask_api = LunataskAPI(self.config.lunatask_api_token)
        except (HTTPError, RequestException) as ex:
            print(f"Unable to connect to Lunatask API: {ex}")
            raise SystemExit(os.EX_IOERR) from ex

    def add_label_reminder(self: Self) -> None:
        """Create a tasks in each area listing tasks that had Labels."""
        for area in self.labelled_tasks:
            labelled = [
                f"- [ ] {x.content} 🏷️ {self.format_task_labels(x)}"
                for x in self.labelled_tasks[area]
            ]
            labelled.sort()

            label_note = f"""These tasks had Labels in Todoist. You can:

* Create Goals to match the original labels and add these tasks to the
  appropriate Goals. **OR,**
* Ignore this and complete this task. ☺️

## Tasks with Labels

{"\n".join(labelled)}
"""

            now = datetime.datetime.now(tz=datetime.UTC)
            new_task = NewTask(
                area_id=area,
                eisenhower=Eisenhower.URGENT_NOT_IMPORTANT,
                motivation=Motivation.SHOULD,
                name=self.config.todoist_label_reminder,
                note=label_note,
                priority=Priority.HIGH,
                scheduled_on=now,
                source="todoist2lunatask",
                source_id=f"labelled-task-reminder {now.isoformat()}",
                status=Status.NEXT,
            )
            try:
                _ = self.luntask_api.create_task(new_task)
            except HTTPError as ex:
                print(
                    f"Unable to labelled task list in '{area}': {ex.response.status_code}"  # noqa: E501
                )
                continue
            except RequestException as ex:
                if ex.response:
                    print(
                        f"Unable to labelled task list in '{area}': {ex.response.status_code}"  # noqa: E501
                    )
                else:
                    print(f"Unable to labelled task list in '{area}': no response")
                continue

    def add_recurring_reminder(self: Self) -> None:
        """Create a tasks in each area listing tasks that had recurring dates."""
        for area in self.recurring_tasks:
            recurring = [
                f"- [ ] {x.content}: {self.format_task_due(x)}"
                for x in self.recurring_tasks[area]
            ]
            recurring.sort()

            recurring_note = f"""These tasks were Recurring in Todoist. You can:

* Add recurrence to their due dates
  (<https://lunatask.app/docs/features/tasks/recurring-tasks>). **OR,**
* Ignore their recurrence and complete this task. 😟

## Recurring Tasks

{"\n".join(recurring)}
"""

            now = datetime.datetime.now(tz=datetime.UTC)
            new_task = NewTask(
                area_id=area,
                eisenhower=Eisenhower.URGENT_IMPORTANT,
                motivation=Motivation.SHOULD,
                name=self.config.todoist_recurring_reminder,
                note=recurring_note,
                priority=Priority.HIGH,
                scheduled_on=now,
                source="todoist2lunatask",
                source_id=f"recurring-task-reminder {now.isoformat()}",
                status=Status.NEXT,
            )
            try:
                _ = self.luntask_api.create_task(new_task)
            except HTTPError as ex:
                print(
                    f"Unable to labelled task list in '{area}': {ex.response.status_code}"  # noqa: E501
                )
                continue
            except RequestException as ex:
                if ex.response:
                    print(
                        f"Unable to labelled task list in '{area}': {ex.response.status_code}"  # noqa: E501
                    )
                else:
                    print(f"Unable to labelled task list in '{area}': no response")
                continue

    def area_for(self: Self, project_id: str) -> uuid.UUID:
        """Return the appropriate Area ID for a Todoist Project."""
        return self.config.todoist_project_map.get(
            self.project_map[project_id].name, self.config.todoist_default_area
        )

    def format_task_comments(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's comments."""
        if task.id not in self.task_comments:
            return ""

        comment_list = []
        posted_at = ""
        for comment in self.task_comments[task.id]:
            lines = [
                self.config.markdown_templates["task-comment-list"].format(comment=x)
                for x in comment.content.split("\n")
            ]
            if comment.posted_at:
                posted_at = self.config.markdown_templates["task-comment-list"].format(
                    comment=f"{comment.posted_at.isoformat()}"
                )
                lines.insert(0, posted_at)
            comment_list.append("\n".join(lines))

        return "\n" + self.config.markdown_templates["task-comments"].format(
            comment_list="\n".join(comment_list),
        )

    def format_task_deadline(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's deadline'."""
        if not task.deadline:
            return ""

        return "\n" + task.deadline.date.isoformat()

    def format_task_description(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's description."""
        return task.description

    def format_task_due(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's due date'."""
        if not task.due:
            return ""

        return "\n" + self.config.markdown_templates["task-due"].format(
            arbitrary=f" ({task.due.string})" if task.due.string else "",
            due_date=task.due.date.isoformat(),
            recurring="🔁" if task.due.is_recurring else "",
        )

    def format_task_labels(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's labels'."""
        if not task.labels or len(task.labels) < 1:
            return ""

        label_list = [
            self.config.markdown_templates["task-label-list"].format(
                colour=self.label_map[x].color,
                favourite="⭐" if self.label_map[x].is_favorite else "",
                name=self.label_map[x].name,
            )
            for x in task.labels
        ]

        return "\n" + self.config.markdown_templates["task-labels"].format(
            label_list=", ".join(label_list)
        )

    def format_task_parent(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's parent."""
        if not task.parent_id:
            return ""

        parent = self.task_map[task.parent_id]
        return "\n" + self.config.markdown_templates["task-parent"].format(
            area=self.project_map[parent.project_id].name,
            name=parent.content,
            priority_glyph=self.glyph_for_priority(parent.priority),
        )

    def format_task_reference(self: Self, task: TodoistModels.Task) -> str:
        """Format a sub-task or parent task as a string.

        Lunatask doesn't support sub-tasks as full tasks, so the sub-task and
        the parent will refer to each other using this format.
        """
        return self.config.markdown_templates["sub-task"].format(
            area=self.area_for(task.project_id),
            name=task.content,
            priority_glyph=self.glyph_for_priority(task.priority),
        )

    def format_task_section(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's section'."""
        if not task.section_id:
            return ""

        return "\n" + self.config.markdown_templates["task-section"].format(
            name=self.section_map[task.section_id]
        )

    def format_task_subtasks(self: Self, task: TodoistModels.Task) -> str:
        """Format a task's subtasks."""
        if task.id not in self.subtasks:
            return ""

        subtask_list = [
            self.config.markdown_templates["task-subtask-list"].format(
                area=self.project_map[x.project_id].name,
                name=x.content,
                priority_glyph=self.glyph_for_priority(x.priority),
            )
            for x in self.subtasks[task.id]
        ]
        return "\n" + self.config.markdown_templates["task-subtasks"].format(
            subtask_list="\n".join(subtask_list)
        )

    def glyph_for_priority(self: Self, priority: int) -> str:
        """Todoist priority is an int from 1 (normal) to 4 (highest)."""
        return self.config.priority_glyph[PRIORITY_VALUE[priority]]

    def import_labels(self: Self) -> int:
        """Import Todoist Labels as Lunatask Goals."""
        # Currently no API for creating Goals.
        raise NotImplementedError

    def task_order(self: Self, order: int) -> None:
        """Translate Todoist Task order."""
        # Currently no way to re-order tasks in Lunatask.
        raise NotImplementedError

    def import_users(self: Self) -> int:
        """Import Todoist Users as Lunatask People."""
        # Currently no supported API for getting User data.
        raise NotImplementedError

    def import_tasks(self: Self) -> int:
        """Import Todoist tasks into Lunatask."""
        print("Collecting Todoist data…")
        retval = self.load_todoist_data()
        if retval != os.EX_OK:
            return retval

        # Transform and load tasks.
        created_tasks = 0
        for task in self.tasks:
            new_task: NewTask = self.newtask_from_task(task)
            try:
                _ = self.luntask_api.create_task(new_task)
                created_tasks += 1
            except HTTPError as ex:
                print(
                    f"Unable to create task '{task.content}': {ex.response.status_code}"
                )
                continue
            except RequestException as ex:
                if ex.response:
                    print(
                        f"Unable to create task '{task.content}': {ex.response.status_code}"  # noqa: E501
                    )
                else:
                    print(f"Unable to create task '{task.content}': no response")
                continue

        print(f"{created_tasks} tasks created in Luntask.")

        print(f"Creating label reminders in {len(self.labelled_tasks)} areas…")
        self.add_label_reminder()

        print(f"Creating recurring task reminders in {len(self.labelled_tasks)} areas…")
        self.add_recurring_reminder()

        return os.EX_OK

    def load_todoist_data(self: Self) -> int:  # noqa: PLR0912
        """Load your existing data from Todoist."""
        try:
            # Originally these APIs returned a list; now it's an iterator that
            # returns a list of things each time.
            self.labels = [x for xs in self.todoist_api.get_labels() for x in xs]
            self.projects = [x for xs in self.todoist_api.get_projects() for x in xs]
            self.sections = [x for xs in self.todoist_api.get_sections() for x in xs]
            self.tasks = [x for xs in self.todoist_api.get_tasks() for x in xs]

            self.label_map = {label.name: label for label in self.labels}
            self.project_map = {project.id: project for project in self.projects}
            self.section_map = {section.id: section for section in self.sections}
            self.task_map = {task.id: task for task in self.tasks}

            for task in self.tasks:
                task_area = self.area_for(task.project_id)
                if task.labels:
                    if task_area in self.labelled_tasks:
                        self.labelled_tasks[task_area].append(task)
                    else:
                        self.labelled_tasks[task_area] = [task]

                if task.due and task.due.is_recurring:
                    if task_area in self.recurring_tasks:
                        self.recurring_tasks[task_area].append(task)
                    else:
                        self.recurring_tasks[task_area] = [task]

                try:
                    for comment_block in self.todoist_api.get_comments(task_id=task.id):
                        for comment in comment_block:
                            if task.id in self.task_comments:
                                self.task_comments[task.id].append(comment)
                            else:
                                self.task_comments[task.id] = [comment]
                except HTTPError as ex:
                    print(f"Error loading comments for {task.id}: {ex}")
                    continue  # THE HORROR; the API should just return []!

        except (HTTPError, RequestException) as ex:
            print(f"Unable to load Todoist data: {ex}")
            return os.EX_IOERR

        # Find subtasks.
        self.subtasks: dict[str, list[TodoistModels.Task]] = {}
        for task in self.tasks:
            if task.parent_id:
                if task.parent_id in self.subtasks:
                    self.subtasks[task.parent_id].append(task)
                else:
                    self.subtasks[task.parent_id] = [task]

        self.show_todoist_data()
        return os.EX_OK

    def newtask_from_task(self: Self, task: TodoistModels.Task) -> NewTask:
        """Create a prototype NewTask for importing into Lunatask."""
        estimate = None
        if task.duration:
            match task.duration.unit:
                case "minute":
                    estimate = task.duration.amount
                case "day":
                    estimate = task.duration.amount * DAY_MINUTES
                case _:
                    # That's an invalid unit.
                    estimate = 0

        # The note is a dumping ground for all the bits that aren't directly
        # convertible from Todoist to Lunatask.
        #
        # The sections are arranged in the new task's notes in this order:
        #
        # - description
        # - section
        # - labels
        # - due
        # - deadline
        # - parent
        # - subtasks
        # - comments
        note = "\n".join(
            [
                x
                for x in [
                    self.format_task_description(task),
                    self.format_task_section(task),
                    self.format_task_labels(task),
                    self.format_task_due(task),
                    self.format_task_deadline(task),
                    self.format_task_parent(task),
                    self.format_task_subtasks(task),
                    self.format_task_comments(task),
                ]
                if x
            ]
        )

        source = None
        source_id = None
        if self.config.todoist_task_source:
            source = self.config.todoist_task_source
            source_id = task.id

        status = Status.LATER
        if task.due:
            delta = (
                cast("datetime.date", task.due.date)
                - datetime.datetime.now(tz=datetime.UTC).date()
            )
            if delta.days <= self.config.todoist_upcoming_days:
                status = Status.NEXT

        return NewTask(
            area_id=self.area_for(task.project_id),
            completed_at=None,
            eisenhower=Eisenhower.UNCATEGORIZED,
            estimate=estimate,
            goal_id=None,
            motivation=Motivation.UNKNOWN,
            name=task.content,
            note=note,
            priority=self.priority_for(task.priority),  # pyright: ignore [reportArgumentType]
            scheduled_on=self.scheduled_for(task),
            source=source,
            source_id=source_id,
            status=status,
        )

    def priority_for(self: Self, priority: int) -> int:
        """Convert Todoist priority into Lunatask priority."""
        return self.config.todoist_priority[PRIORITY_VALUE[priority]]  # pyright: ignore [reportArgumentType]

    def scheduled_for(self: Self, task: TodoistModels.Task) -> datetime.datetime | None:
        """Format a task's due date'."""
        if not task.due:
            return None

        return datetime.datetime.fromisoformat(task.due.date.isoformat())

    def show_todoist_data(self: Self) -> None:
        """Print some info about the data we loaded from Todoist."""
        print("Loaded Tasks from Todoist:")
        print(f"- {len(self.projects)} Projects")
        print(f"- {len(self.tasks)} Tasks:")
        print(
            f"  - {len(self.subtasks)} have {sum([len(self.subtasks[k]) for k in self.subtasks])} sub-Tasks"  # noqa: E501
        )
        print(f"  - {len(self.labels)} Labels")
        print(f"  - {len(self.task_comments)} Comments")
