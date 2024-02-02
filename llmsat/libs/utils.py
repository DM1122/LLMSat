"""Game-related utilities"""

import json
import subprocess
from datetime import datetime, timedelta
from enum import Enum
from string import Template
from typing import Optional

from cmd2 import Cmd2ArgumentParser
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema

epoch = datetime(
    year=1951, month=1, day=1
)  # starting Earth epoch in KSP RSS (DO NOT MODIFY)


class AppConfig(BaseModel):
    model: str
    load_checkpoint: bool
    checkpoint_name: str
    port: int


def is_ksp_running():
    """Determine whether Kerbal Space Program is currently running on the system."""
    try:
        # List processes and grep for KSP
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8")
        return "KSP" in output
    except:
        return False


def load_checkpoint(name: str, space_center):
    """Load the given game save state"""
    try:
        space_center.load(name)
    except ValueError:
        raise ValueError(
            f"No checkpoint named '{name}.sfs' was found. Please create one"
        )


class MET:  # TODO: rename
    def __init__(self, seconds):
        """Mission elapsed time object.

        Args:
            seconds: seconds since the mission began
        """
        self.seconds = int(seconds)

    def __str__(self):
        # Constants for time calculations
        seconds_in_minute = 60
        seconds_in_hour = 3600
        seconds_in_day = 86400
        seconds_in_year = 31536000  # Approximation, not accounting for leap years

        # Calculate years, days, hours, minutes, and seconds
        years, remaining_seconds = divmod(self.seconds, seconds_in_year)
        days, remaining_seconds = divmod(remaining_seconds, seconds_in_day)
        hours, remaining_seconds = divmod(remaining_seconds, seconds_in_hour)
        minutes, seconds = divmod(remaining_seconds, seconds_in_minute)

        return f"T+ {years:01}Y, {days:03}D, {hours:02}:{minutes:02}:{seconds:02}"


def ksp_ut_to_datetime(ut: float) -> datetime:
    """Translates a given KSP universal time to a datetime object with the correct epoch offset."""
    return epoch + timedelta(seconds=ut)


class CustomCmd2ArgumentParser(Cmd2ArgumentParser):
    def __init__(self, cmd_instance_method, *args, **kwargs):
        """Custom parser to pipe output to poutput so the agent can process these messages."""
        super().__init__(*args, **kwargs)
        self.cmd_instance_method = cmd_instance_method

    def _print_message(self, message, file=None):
        if message:
            # Use cmd2's poutput instead of writing directly to sys.stderr or sys.stdout
            self.cmd_instance_method().poutput(message)


class CustomGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)
        print(json.dumps(json_schema, indent=4))
        reduced_schema = json_schema["$defs"]

        primary_key = list(reduced_schema.keys())[0]
        reduced_schema[primary_key].pop("required", None)
        del reduced_schema[primary_key]["title"]

        if "properties" in reduced_schema[primary_key]:
            for property in reduced_schema[primary_key]["properties"]:
                reduced_schema[primary_key]["properties"][property].pop("title", None)

        return reduced_schema


def format_return_obj_str(obj: BaseModel, template: Template = None):
    """Formats a pydantic object as a return schema string for a cmd2 argument parser epilog. Template must have $obj"""

    statement = "Returns:\n"

    obj_schema = json.dumps(obj.model_json_schema(), indent=4)

    if template:
        output = statement + template.substitute(obj=obj_schema)

    else:
        output = statement + obj_schema

    return output


class MessageType(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    COMMAND = "command"


class Message(BaseModel):
    type: MessageType
    data: Optional[str] = None
