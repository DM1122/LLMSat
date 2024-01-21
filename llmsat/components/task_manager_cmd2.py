import json
from datetime import datetime

import cmd2


class TaskManager(cmd2.CommandSet):
    def __init__(self):
        super().__init__()
        self.task_file = (
            "tasks.json"  # Path to the JSON file where tasks will be stored
        )

    def read_tasks_file(self):
        try:
            with open(self.task_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def write_tasks_file(self, tasks):
        with open(self.task_file, "w") as file:
            json.dump(tasks, file, indent=4)

    def do_add_task(self, task_name, description, date_str):
        try:
            due_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use 'YYYY-MM-DD'.")
            return

        new_task = {
            "name": task_name,
            "description": description,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "completed": False,
        }

        tasks = self.read_tasks_file()
        tasks.append(new_task)
        self.write_tasks_file(tasks)
        print(f"Task '{task_name}' added successfully.")

    def do_read_tasks(self, _):
        tasks = self.read_tasks_file()
        if not tasks:
            print("No tasks found.")
            return

        for i, task in enumerate(tasks, 1):
            print(f"Task {i}:")
            print(f"  Name: {task['name']}")
            print(f"  Description: {task['description']}")
            print(f"  Due Date: {task['due_date']}")
            print(f"  Completed: {'Yes' if task['completed'] else 'No'}")
            print("-" * 20)

    def do_complete_task(self, task_name):
        tasks = self.read_tasks_file()
        found = False

        for task in tasks:
            if task["name"] == task_name:
                task["completed"] = True
                found = True
                break

        if found:
            self.write_tasks_file(tasks)
            print(f"Task '{task_name}' marked as completed.")
        else:
            print(f"Task '{task_name}' not found.")

    def do_delete_task(self, task_name):
        tasks = self.read_tasks_file()
        new_tasks = [task for task in tasks if task["name"] != task_name]

        if len(new_tasks) == len(tasks):
            print(f"Task '{task_name}' not found.")
            return

        self.write_tasks_file(new_tasks)
        print(f"Task '{task_name}' has been deleted.")

    def do_edit_task(self, args):
        args = args.split()  # Split the input arguments

        if len(args) < 1:
            print("Please provide the current name of the task.")
            return

        current_name = args[0]
        new_name = args[1] if len(args) > 1 else None
        new_description = args[2] if len(args) > 2 else None
        new_due_date = args[3] if len(args) > 3 else None

        tasks = self.read_tasks_file()
        found = False

        for task in tasks:
            if task["name"] == current_name:
                if new_name:
                    task["name"] = new_name
                if new_description:
                    task["description"] = new_description
                if new_due_date:
                    try:
                        task["due_date"] = datetime.strptime(
                            new_due_date, "%Y-%m-%d"
                        ).strftime("%Y-%m-%d")
                    except ValueError:
                        print("Invalid date format. Please use 'YYYY-MM-DD'.")
                        return
                found = True
                break

        if found:
            self.write_tasks_file(tasks)
            print(f"Task '{current_name}' has been updated.")
        else:
            print(f"Task '{current_name}' not found.")


# ... [Rest of the class]
