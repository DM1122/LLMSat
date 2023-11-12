from pathlib import Path

import cmd2
import krpc
from decouple import config

from llmsat import utils
from llmsat.components.autpilot import AutopilotService
from llmsat.components.spacecraft_manager import SpacecraftManager

CHECKPOINT_NAME = "checkpoint"


class App(cmd2.Cmd):
    """Command line interface."""

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

    def preloop(self):
        super().preloop()
        self.poutput("Welcome to SatelliteOS")
        self.do_help("-v")


if __name__ == "__main__":
    if not utils.is_ksp_running():
        ksp_path = Path(str(config("KSP_PATH")))
        print(f"Launching KSP from '{ksp_path}'...")
        utils.launch_ksp(path=ksp_path)

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    connection = krpc.connect(name="Simulator")

    print(f"Loading '{CHECKPOINT_NAME}.sfs' checkpoint...")
    utils.load_checkpoint(name=CHECKPOINT_NAME, space_center=connection.space_center)

    spacecraft_manager = SpacecraftManager(connection)
    autopilot_service = AutopilotService(connection)
    app = App(command_sets=[spacecraft_manager, autopilot_service])
    app.cmdloop()
