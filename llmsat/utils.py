"""Game-related utilities"""

import functools
import inspect
import json
import os
import subprocess
from pathlib import Path

from pydantic import BaseModel


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
