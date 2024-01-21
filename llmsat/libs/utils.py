"""Game-related utilities"""

import argparse
import functools
import inspect
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

import cmd2
from cmd2 import Cmd2ArgumentParser, ansi, with_argparser
from pydantic import BaseModel, Field

epoch = datetime(
    year=1951, month=1, day=1
)  # starting Earth epoch in KSP RSS (DO NOT MODIFY) Need to set


def is_ksp_running():
    """Determine whether Kerbal Space Program is currently running on the system."""
    try:
        # List processes and grep for KSP
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8")
        return "KSP" in output
    except:
        return False


def launch_ksp(path: Path):
    subprocess.Popen([path], cwd=os.path.dirname(path))


def load_checkpoint(name: str, space_center):
    """Load the given game save state"""
    try:
        space_center.load(name)
    except ValueError as e:
        raise ValueError(
            f"No checkpoint named '{name}.sfs' was found. Please create one"
        )


def load_json(filename):
    """Load a given JSON file"""

    with open(filename, "r") as file:
        data = json.load(file)
    return data


class MET:  # TODO: rename
    def __init__(self, seconds):
        """Mission elapsed time object.

        Args:
            seconds: seconds since the mission began
        """
        self.seconds = int(seconds)
        print(self.seconds)

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


def get_ut(connection) -> datetime:
    """Get the current in-game universal time"""
    return epoch + timedelta(seconds=connection.space_center.ut)


class CustomCmd2ArgumentParser(Cmd2ArgumentParser):
    def __init__(self, cmd_instance_method, *args, **kwargs):
        """Custom parser to pipe output to poutput so the agent can process these messages."""
        super().__init__(*args, **kwargs)
        self.cmd_instance_method = cmd_instance_method

    def _print_message(self, message, file=None):
        if message:
            # Use cmd2's poutput instead of writing directly to sys.stderr or sys.stdout
            self.cmd_instance_method().poutput(message)
