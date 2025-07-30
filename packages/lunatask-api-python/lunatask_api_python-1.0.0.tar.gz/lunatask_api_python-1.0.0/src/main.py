"""Import your tasks from Todoist to Lunatask."""

import argparse
import os
import sys
import uuid
from tomllib import TOMLDecodeError

from requests import HTTPError, RequestException
from todoist_api_python.api import TodoistAPI

from config import (
    Config,
    MissingPriorityError,
    TokenInvalidCharacterError,
    TokenLengthError,
)
from importer import TodoistImporter
from lunatask.api import LunataskAPI
from lunatask.models.people import NewPerson, Relationship
from lunatask.models.source import Source
from lunatask.models.task import NewTask


def _check_ready(config: Config) -> int:
    """Check if we're ready to go.

    Creates API objects, ensures they work, and reports on whether you've got
    a full set of Todoist Projects listed in your project mapping.
    """
    try:
        lunatask_api = LunataskAPI(config.lunatask_api_token)
        _ = lunatask_api.ping()
    except HTTPError as ex:
        print(f"Unable to connect to Lunatask API: {ex}")
        return os.EX_IOERR

    print("Successfully connected to Lunatask API.")

    try:
        todoist_api = TodoistAPI(config.todoist_api_token)
        projects = [x for xs in todoist_api.get_projects() for x in xs]
    except HTTPError as ex:
        print(f"Unable to connect to Todoist API: {ex}")
        return os.EX_IOERR

    print("Successfully connected to Todoist API.")

    warned = 0
    for project in projects:
        if project.name not in config.todoist_project_map:
            warned += 1
            print(f"Warning: '{project.name}' not mapped to a Lunatask Area.")

    if warned > 0:
        print(f"Found {len(projects)} Todoist projects. {warned} not mapped.")
    else:
        print(f"Found {len(projects)} Todoist projects mapped to Lunatask Areas.")

    return os.EX_OK


def _live_test_tasks(config: Config, api: LunataskAPI, uuid_str: str) -> None:
    """Run a live test of the Task APIs."""
    test_task = None
    try:
        print("Creating task.")
        test_task = api.create_task(
            NewTask(
                config.todoist_default_area,
                name=uuid_str,
            ),
            source=Source("todoist2lunatask", "live test"),
        )

        try:
            print("Updating task.")
            test_task = api.update_task(test_task, "New Name", "A task note.")
        except RequestException as ex:
            print(f"Unable to update task: {ex.response}")

        try:
            print("Get task.")
            _ = api.get_task(test_task.id)
        except RequestException as ex:
            print(f"Unable to get task: {ex.response}")

        try:
            print("Get tasks.")
            _ = api.get_tasks(Source("todoist2lunatask", "live test"))
        except RequestException as ex:
            print(f"Unable to get tasks: {ex.response}")

    except RequestException as ex:
        print(f"Unable to test Task APIs: {ex.response}")
    finally:
        if test_task:
            try:
                print("Delete task.")
                _ = api.delete_task(test_task.id)
            except RequestException as ex:
                print(f"Unable to delete test task: {ex.response}")


def _list_test_person(config: Config, api: LunataskAPI, uuid_parts: list[str]) -> None:
    """Run a live test of the People APIs.

    This exercises parts of the Lunatask API that aren't used to import
    Todoist tasks.
    """
    test_person = None
    try:
        print("Creating person.")
        test_person = api.create_person(
            NewPerson(
                uuid_parts[0],
                uuid_parts[-1],
                Relationship.ALMOST_STRANGERS,
                "todoist2lunatask",
                "live test",
            )
        )

        try:
            print("Get person.")
            _ = api.get_person(test_person.id)
        except RequestException as ex:
            print(f"Get person failed: {ex.response}")

        try:
            print("Get people.")
            _ = api.get_people(Source("todoist2lunatask", "live test"))
        except RequestException as ex:
            print(f"Get people failed: {ex.response}")

        try:
            print("Create person timeline note.")
            _ = api.create_timeline_note(test_person.id, content="Hello, world.")
        except RequestException as ex:
            print(f"Couldn't add a person timeline note: {ex.response}")

    except RequestException as ex:
        print(f"Unable to test People APIs: {ex.response}")
    finally:
        if test_person:
            try:
                print("Deleting person.")
                _ = api.delete_person(test_person.id)
            except RequestException as ex:
                print(f"Unable to delete test person: {ex.response}")


def _live_test(config: Config) -> int:
    """Run a live test.

    This exercises the Lunatask API by creating Tasks, Notes, People and Person
    Timeline Notes, updating the Tasks, attempting to track a Habit, and
    deleting the Tasks and People. This is done in the todoist_default_area
    specified in your config file.
    """
    # Check authentication.
    try:
        api = LunataskAPI(config.lunatask_api_token)
        print("Attempting authentication.")
        _ = api.ping()
    except HTTPError as ex:
        print(f"\tFailed to authenticate: {ex}")
        return os.EX_NOUSER

    uuid_str = str(uuid.uuid1())
    uuid_parts = uuid_str.split("-")

    # Task APIs
    _live_test_tasks(config, api, uuid_str)

    # People APIs
    #
    # - people API
    # - person timeline note
    _list_test_person(config, api, uuid_parts)

    # TODO: Things we can't currently test; these need an existing  # noqa: FIX002
    # target habit or notebook, and there's currently no API for creating those.
    #
    # needs existing habit
    # - habit tracking
    #
    # needs existing notebook
    # - note creation

    return os.EX_OK


def _show_projects(config: Config) -> int:
    """Pretty-print Todoist Projects."""
    # TODO: Make this user-friendly instead of dev-friendly.  # noqa: FIX002
    try:
        todoist_api = TodoistAPI(config.todoist_api_token)
        projects = [x for xs in todoist_api.get_projects() for x in xs]

        print("Projects:")
        for project in projects:
            print(f"\t'{project.name}' = {project}'")
    except HTTPError as ex:
        print(f"Unable to read Todoist Projects: {ex}")
        return os.EX_IOERR

    return os.EX_OK


def _show_labels(config: Config) -> int:
    """Pretty-print Todoist Labels."""
    # TODO: Make this user-friendly instead of dev-friendly.  # noqa: FIX002
    try:
        todoist_api = TodoistAPI(config.todoist_api_token)
        labels = [x for xs in todoist_api.get_labels() for x in xs]

        print("Labels:")
        for label in labels:
            print(f"\t'{label.name}' = {label}")
    except HTTPError as ex:
        print(f"Unable to read Todoist Labels: {ex}")
        return os.EX_IOERR

    return os.EX_OK


def main() -> int:
    """Import your tasks from Todoist to Lunatask.

    `todoist2lunatask --help` for details, and read the
    [`todoist2lunatask.config`](https://codeberg.org/Taffer/todoist2lunatask/src/branch/main/todoist2lunatask.config.template)
    template.
    """
    parser = argparse.ArgumentParser(
        prog="todoist2lunatask",
        description="Import tasks/projects/labels from Todoist into Lunatask",
        epilog="You must create a todoist2lunatask.config file by copying "
        "todoist2lunatask.config.template and editing it. Please read the "
        "README.md for details.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check API tokens and Project map.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        default="todoist2lunatask.config",
        help="Specify the configuration file.",
    )
    parser.add_argument(
        "--import",
        dest="do_import",
        action="store_true",
        help="Import Todoist Tasks into Lunatask.",
    )
    parser.add_argument(
        "--show-labels",
        action="store_true",
        help="List your Todoist Labels.",
    )
    parser.add_argument(
        "--show-projects",
        action="store_true",
        help="List your Todoist Projects.",
    )
    parser.add_argument(
        "--live-test",
        action="store_true",
        help="Run a live test; this exercises the Lunatask API by creating "
        "Tasks, Notes, People and Person Timeline Notes, updating the Tasks, "
        "attempting to track a Habit, and deleting the Tasks and People. "
        "This is done in the todoist_default_area specified in your config "
        "file.",
    )
    args = parser.parse_args()

    # Load configuration
    config = None
    try:
        tmp = Config.from_toml_file(args.config)
        config = tmp[0] if isinstance(tmp, list) else tmp
    except MissingPriorityError as ex:
        print(f"Missing Todoist priority level in {args.config}:")
        print(f"\t{ex}")
        sys.exit(os.EX_DATAERR)
    except TokenLengthError as ex:
        print(f"Invalid token length in {args.config}:")
        print(f"\t{ex}")
        sys.exit(os.EX_DATAERR)
    except TokenInvalidCharacterError as ex:
        print(f"Invalid token character in {args.config}:")
        print(f"\t{ex}")
        sys.exit(os.EX_DATAERR)
    except TOMLDecodeError as ex:
        print(f"Invalid config file {args.config}: {ex}")
        sys.exit(os.EX_OSFILE)

    if args.check:
        sys.exit(_check_ready(config))

    if args.do_import:
        importer = TodoistImporter(config)
        sys.exit(importer.import_tasks())

    if args.live_test:
        sys.exit(_live_test(config))

    if args.show_projects:
        sys.exit(_show_projects(config))

    if args.show_labels:
        sys.exit(_show_labels(config))

    parser.print_help()
    sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
