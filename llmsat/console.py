"""Spacecraft Console App"""

import json
import logging
import threading
from pathlib import Path

import cmd2
import krpc
import zmq
import zmq.asyncio

from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autopilot import AutopilotService
from llmsat.components.comms_service import CommunicationService
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.orbit_propagator import OrbitPropagator
from llmsat.components.spacecraft_manager import SpacecraftManager
from llmsat.components.task_manager import TaskManager
from llmsat.libs import utils

CONFIG_PATH = Path("llmsat/app_config.json")


class Console(cmd2.Cmd):
    """Spacecraft console app"""

    def __init__(self, port: int, quiet=False, *args, **kwargs):
        super().__init__(include_py=True, *args, **kwargs)

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
        del cmd2.Cmd.do_set

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

        # start server for controller
        self.controller_connected = False
        self.context = zmq.Context()
        self.controller_connection = self.context.socket(zmq.PAIR)
        self.controller_connection.bind(f"tcp://*:{port}")
        receive_thread = threading.Thread(
            name="console-receive-message", target=self.receive_message, daemon=True
        )
        receive_thread.start()

    def receive_message(self):
        """Receive and execute command messages from the controller."""
        while True:
            message: utils.Message = self.controller_connection.recv_pyobj()
            if message.type == utils.MessageType.COMMAND:
                self.on_controller_command(message.data)
            elif message.type == utils.MessageType.CONNECT:
                self.on_controller_connect()
            elif message.type == utils.MessageType.DISCONNECT:
                self.on_controller_disconnect()

    def on_controller_command(self, message):
        print(f"{self.prompt}{message}")
        self.onecmd_plus_hooks(message)
        output = self.get_output()
        self.send_message(output)

    def on_controller_connect(self):
        self.controller_connected = True
        print("Controller connected")
        self.get_output()  # clear buffer
        self.display_dashboard()
        self.send_message(self.get_output())

    def on_controller_disconnect(self):
        self.controller_connected = False
        print("Controller disconnected")

    def send_message(self, message: str):
        """Send message to the controller."""
        self.controller_connection.send_string(message)

    def poutput(self, message="", timestamp=False, *args, **kwargs):
        if timestamp:
            spacecraft_manager = self.find_commandsets(SpacecraftManager)[0]
            ut = spacecraft_manager.get_ut()
            message = f"{ut.isoformat()} | {message}"
        self.output_buffer.append(message)
        if not self.quiet:
            super().poutput(message, *args, **kwargs)

    def async_alert(self, message, *args, **kwargs):
        # self.output_buffer.append(message)
        self.send_message(message)

        super().async_alert(message, *args, **kwargs)

    def perror(self, message, *args, **kwargs):
        self.output_buffer.append(message)
        if not self.quiet:
            super().perror(message, *args, **kwargs)

    def preloop(self):
        super().preloop()
        self.display_dashboard()

    def display_dashboard(self):
        spacecraft_manager = self.find_commandsets(SpacecraftManager)[0]
        task_manager = self.find_commandsets(TaskManager)[0]
        ut = spacecraft_manager.get_ut()
        met = spacecraft_manager.get_met()

        self.poutput("SatelliteOS")
        self.poutput(f"UT: {ut.isoformat()} | MET: {met}")
        self.poutput("")

        spacecraft_manager.do_read_mission_brief()
        self.poutput("")

        self.poutput("Task Plan:")
        tasks = task_manager.read_tasks()  # TODO: do_read_tasks() does not work
        self.poutput(json.dumps(tasks, indent=4, default=lambda o: o.dict()))
        self.poutput("")

        self.poutput("Spacecraft Properties:")
        spacecraft_manager.do_get_spacecraft_properties()
        self.poutput("")

        self.poutput("Resources:")
        spacecraft_manager.do_get_resources()

        self.do_help("-v")

    def get_output(self):
        """Retrieve all output and clear the buffer"""
        output = "\n".join(self.output_buffer)
        self.output_buffer.clear()
        return output


if __name__ == "__main__":
    with open(CONFIG_PATH, "r") as file:
        app_config_data = json.load(file)
        app_config = utils.AppConfig(**app_config_data)

    if not utils.is_ksp_running():
        raise Exception("Please make sure KSP is running")

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    ksp_connection = krpc.connect(name="Client")

    if app_config.load_checkpoint:
        print(f"Loading '{app_config.checkpoint_name}.sfs' checkpoint...")
        utils.load_checkpoint(
            name=app_config.checkpoint_name, space_center=ksp_connection.space_center
        )

    spacecraft_manager = SpacecraftManager(ksp_connection)
    autopilot_service = AutopilotService(ksp_connection)
    payload_manager = ExperimentManager(ksp_connection)
    communication_service = CommunicationService(ksp_connection)
    task_manager = TaskManager(ksp_connection)
    alarm_manager = AlarmManager(
        ksp_connection, remove_alarms_on_init=app_config.load_checkpoint
    )
    orbit_propagator = OrbitPropagator(ksp_connection)

    app = Console(
        port=app_config.port,
        command_sets=[
            spacecraft_manager,
            autopilot_service,
            payload_manager,
            task_manager,
            communication_service,
            alarm_manager,
            orbit_propagator,
        ],
    )

    app.cmdloop()

    input("Simulation complete. Press any key to quit...")

    ksp_connection.close()
