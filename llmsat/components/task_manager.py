"""Remote sensing manager class."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from string import Template
from typing import Optional

from cmd2 import CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat.libs import utils

TASK_FILE = Path("disk/tasks_file.json")


class TaskStatus(Enum):
    PENDING = "pending"
    PROGRESS = "in progress"
    COMPLETE = "complete"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel, use_enum_values=True):
    """A task"""

    id: int = Field(description="Task unique ID")
    name: str = Field(description="Task statement")
    description: Optional[str] = Field(description="Detailed description")
    start: Optional[datetime] = Field(
        description="Time at which the task should be started"
    )
    end: Optional[datetime] = Field(
        description="Time by which the task should be completed"
    )
    # dependencies: Optional[list[int]] = Field(description="IDs of tasks this task depends on")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")


@with_default_category("TaskManager")
class TaskManager(CommandSet):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        """Task manager class."""
        if TaskManager._initialized:
            return
        super().__init__()

        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel
        self._reset_tasks()

        TaskManager._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return TaskManager()._cmd

    add_task_parser = utils.CustomCmd2ArgumentParser(_get_cmd_instance)
    add_task_parser.add_argument(
        "-name",
        type=str,
        required=True,
        help="Task name",
    )
    add_task_parser.add_argument(
        "-desc",
        type=str,
        required=False,
        help="Task description",
    )
    add_task_parser.add_argument(
        "-start",
        type=str,
        required=False,
        help="Task start universal time YYYY-MM-DDTHH:MM:SS",
    )
    add_task_parser.add_argument(
        "-end",
        type=str,
        required=False,
        help="Task end universal time YYYY-MM-DDTHH:MM:SS",
    )

    @with_argparser(add_task_parser)
    def do_add_task(self, args):
        """Add a new task"""
        date_format = "%Y-%m-%dT%H:%M:%S"

        start = datetime.strptime(args.start, date_format) if args.end else None
        end = datetime.strptime(args.end, date_format) if args.end else None
        output = self.add_task(
            name=args.name,
            description=args.desc,
            start=start,
            end=end,
        )
        self._cmd.poutput(f"Task {output.id}:'{output.name}' created")

    def add_task(
        self,
        name: str,
        description: str = None,
        start: datetime = None,
        end: datetime = None,
    ) -> Task:
        """Add a new task"""

        tasks = self.read_tasks()
        id = max(tasks.keys(), default=0) + 1
        task = Task(id=id, name=name, description=description, start=start, end=end)
        tasks[id] = task
        self._write_tasks(tasks)

        return task

    read_tasks_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        epilog=utils.format_return_obj_str(Task, Template("dict[int,$obj]")),
    )

    @with_argparser(read_tasks_parser)
    def do_read_tasks(self, _=None):
        """Read existing tasks"""
        output = self.read_tasks()

        self._cmd.poutput(json.dumps(output, indent=4, default=lambda o: o.dict()))

    def read_tasks(self) -> dict[int, Task]:
        """Reads task from database"""
        with open(TASK_FILE, "r") as file:
            data = json.load(file)

        tasks = {int(k): Task(**v) for k, v in data.items()}

        return tasks

    set_task_status_parser = utils.CustomCmd2ArgumentParser(_get_cmd_instance)
    set_task_status_parser.add_argument(
        "-id",
        type=int,
        required=True,
        help="Task ID",
    )
    set_task_status_parser.add_argument(
        "-status",
        type=str,
        required=True,
        help="New status",
    )

    @with_argparser(set_task_status_parser)
    def do_set_task_status(self, args):
        """Set a task's status"""

        try:
            status = TaskStatus(args.status)
        except ValueError:
            raise ValueError(
                f"'{args.status}' is not a valid TaskStatus. Must be one of: {[status.value for status in TaskStatus]}"
            )

        output = self.set_task_status(id=args.id, status=status)

        self._cmd.poutput(f"Set task {output.id} status to: {output.status.value}")

    def set_task_status(self, id: int, status: TaskStatus) -> Task:
        """Set a task's status"""
        tasks = self.read_tasks()
        tasks[id].status = status

        self._write_tasks(tasks)

        return tasks[id]

    def _write_tasks(self, tasks: dict[int, Task]):
        """Write tasks object to file"""
        tasks_serial = {k: v.model_dump(mode="json") for k, v in tasks.items()}
        with open(TASK_FILE, "w") as file:
            json.dump(tasks_serial, file, indent=4)

    def _reset_tasks(self):
        """Resets the task file to an empty JSON file."""
        with open(TASK_FILE, "w") as file:
            json.dump({}, file, indent=4)
