"""Spacecraft Console App"""
import json
import logging
import time
from pathlib import Path

import cmd2
import krpc
from decouple import config
from langchain.tools import tool
from langchain.tools.base import ToolException
from pydantic import BaseModel

from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autpilot import AutopilotService
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.spacecraft_manager import SpacecraftManager
from llmsat.libs import utils


class AgentCMDInterface:
    """Tool interface between LLM and cmd2 app"""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AgentCMDInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, app=None):
        if AgentCMDInterface._initialized:
            return
        self.app = app
        self.app.preloop()
        AgentCMDInterface._initialized = True

    @staticmethod
    def _get_instance():
        instance = AgentCMDInterface()
        if instance.app is None:
            raise ValueError(
                "AgentCMDInterface must be initialized with a cmd2 app before calling its methods."
            )
        return AgentCMDInterface()

    @staticmethod
    @tool()
    def run(input: str) -> str:
        """Write a command to the console"""
        app = AgentCMDInterface._get_instance().app

        app.onecmd_plus_hooks(input)

        output = app.get_output()

        return output


class Console(cmd2.Cmd):
    """Spacecraft console app"""

    def __init__(self, quiet=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.intro = "SatelliteOS"
        self.prompt = "> "
        self.quiet = quiet

        # delete built-in commands and settings
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_shortcuts
        del cmd2.Cmd.do_edit
        del cmd2.Cmd.do_history
        del cmd2.Cmd.do_quit
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_shell

        self.remove_settable("allow_style")
        self.remove_settable("always_show_hint")
        self.remove_settable("debug")
        self.remove_settable("echo")
        self.remove_settable("editor")
        self.remove_settable("feedback_to_output")
        self.remove_settable("max_completion_items")
        self.remove_settable("quiet")
        self.remove_settable("timing")

        self.default_category = "Built-in Commands"

        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.output_buffer = []

    def poutput(self, message, *args, **kwargs):
        # logging.info(f"Output: {message}")
        self.output_buffer.append(message)

        if not self.quiet:
            super().poutput(message, *args, **kwargs)

    def perror(self, message, *args, **kwargs):
        self.output_buffer.append(message)
        if not self.quiet:
            super().perror(message, *args, **kwargs)

    def preloop(self):
        super().preloop()
        self.display_dashboard()

    def display_dashboard(self):
        spacecraft_manager = self.find_commandsets(SpacecraftManager)[0]
        ut = spacecraft_manager.get_ut()
        met = spacecraft_manager.get_met()

        self.poutput(f"SatelliteOS")
        self.poutput(f"UT: {ut.isoformat()} | MET: {met}")
        self.poutput("\n")
        spacecraft_manager.do_read_mission_brief()
        spacecraft_manager.do_get_spacecraft_properties()
        spacecraft_manager.do_get_resources()

        self.do_help("-v")

    def get_output(self):
        # Retrieve all output and clear the buffer
        output = "\n".join(self.output_buffer)
        self.output_buffer.clear()
        return output


# if __name__ == "__main__":
#     app = Console()
#     app.cmdloop()
