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

from llmsat import utils
from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autpilot import AutopilotService
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.spacecraft_manager import SpacecraftManager


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

        app.preloop()

        app.onecmd_plus_hooks(input)

        app.postloop()

        # get output somehow

        output = "There atr 6 parts onboard"

        return output


class Console(cmd2.Cmd):
    """Spacecraft console app"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.intro = "SatelliteOS"
        self.prompt = "> "

        # delete built-in commands and settings
        del cmd2.Cmd.do_alias
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_shortcuts
        del cmd2.Cmd.do_edit
        # del cmd2.Cmd.do_history
        # del cmd2.Cmd.do_quit
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

    def poutput(self, message, *args, **kwargs):
        # logging.info(f"Output: {message}")

        # Then call the original poutput function
        super().poutput(message, *args, **kwargs)

    def preloop(self):
        super().preloop()
        self.poutput("Welcome to SatelliteOS\n")
        self.do_get_spacecraft_properties("")
        self.do_help("-v")
