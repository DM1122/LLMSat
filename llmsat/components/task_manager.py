"""Remote sensing manager class."""
import argparse
import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from cmd2 import CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat import utils

TASK_FILE = Path("llmsat/tasks_file.json")


class TaskStatus(Enum):
    PENDING = "pending"
    PROGRESS = "in progress"
    COMPLETE = "complete"


class Task(BaseModel):
    """A task"""

    name: str = Field(description="Task statement")
    description: Optional[str] = Field(description="Detailed description")
    start: Optional[datetime] = Field(
        description="Time at which the task should be started"
    )
    end: Optional[datetime] = Field(
        description="Time by which the task should be completed"
    )
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

        TaskManager._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return TaskManager()._cmd

    def do_add_task(self, statement):
        """Add a new task"""
        output = self.add_task()
        self._cmd.poutput(output)

    def add_task(self, name, description=None, start=None, end=None):
        """Add a new task"""
        task = Task(name=name, description=description, start=start, end=end)

        tasks = self.read_tasks()
        task_id = max(tasks.keys(), default=0) + 1
        tasks[task_id] = task.model_dump(mode="json")
        self._write_tasks(tasks)

        print(f"Created task: '{name}'")

    def do_read_tasks(self, _=None):
        """Reads tasks from database"""
        output = self.read_tasks()
        self._cmd.poutput(output)

    def read_tasks(self) -> dict[int, dict]:
        """Reads task from database"""
        with open(TASK_FILE, "r") as file:
            return json.load(file)

    def do_complete_task(self, statement):
        """Set a task's status to completed"""
        output = self.complete_task()
        self._cmd.poutput(output)

    def complete_task(self):
        """Set a task's status to completed"""
        pass

    def do_edit_task(self, statement):
        """Edit an existing task"""
        output = self.edit_task()
        self._cmd.poutput(output)

    def edit_task(self):
        """Edit an existing task"""
        pass

    def do_delete_task(self, statement):
        """Delete a task"""
        output = self.delete_task()
        self._cmd.poutput(output)

    def delete_task(self):
        """Delete a task"""
        pass

    def _write_tasks(self, tasks):
        """Write tasks object to file"""
        with open(TASK_FILE, "w") as file:
            json.dump(tasks, file, indent=4)
