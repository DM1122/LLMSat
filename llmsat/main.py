"""Runs simulation loop"""

import json

import krpc

from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autpilot import AutopilotService
from llmsat.components.console import Console
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.orbit_propagator import OrbitPropagator
from llmsat.components.spacecraft_manager import SpacecraftManager
from llmsat.components.task_manager import TaskManager
from llmsat.libs import utils

CONFIG_PATH = "llmsat/app_config.json"


if __name__ == "__main__":
    with open(CONFIG_PATH, "r") as file:
        app_config_data = json.load(file)
        app_config = utils.AppConfig(**app_config_data)

    if not utils.is_ksp_running():
        raise Exception("Please make sure KSP is running")

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    connection = krpc.connect(name="Client")

    if app_config.load_checkpoint:
        print(f"Loading '{app_config.checkpoint_name}.sfs' checkpoint...")
        utils.load_checkpoint(
            name=app_config.checkpoint_name, space_center=connection.space_center
        )

    spacecraft_manager = SpacecraftManager(connection)
    autopilot_service = AutopilotService(connection)
    payload_manager = ExperimentManager(connection)
    task_manager = TaskManager(connection)
    alarm_manager = AlarmManager(
        connection, remove_alarms_on_init=app_config.load_checkpoint
    )
    orbit_propagator = OrbitPropagator(connection)

    app = Console(
        command_sets=[
            spacecraft_manager,
            autopilot_service,
            payload_manager,
            task_manager,
            alarm_manager,
            orbit_propagator,
        ]
    )

    app.cmdloop()

    input("Simulation complete. Press any key to quit...")

    connection.close()
