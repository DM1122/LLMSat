"""Runs simulation loop"""

from pathlib import Path

import krpc
import utils
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

from llmsat import utils
from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autpilot import AutopilotService
from llmsat.components.console import AgentCMDInterface, Console
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.orbit_propagator import OrbitPropagator
from llmsat.components.spacecraft_manager import SpacecraftManager
from llmsat.components.task_manager import TaskManager

CHECKPOINT_NAME = "checkpoint"
load_checkpoint = False

if __name__ == "__main__":
    if not utils.is_ksp_running():
        ksp_path = Path(str(config("KSP_PATH")))
        print(f"Launching KSP from '{ksp_path}'...")
        utils.launch_ksp(path=ksp_path)

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    connection = krpc.connect(name="Simulator")

    if load_checkpoint:
        print(f"Loading '{CHECKPOINT_NAME}.sfs' checkpoint...")
        utils.load_checkpoint(
            name=CHECKPOINT_NAME, space_center=connection.space_center
        )

    spacecraft_manager = SpacecraftManager(connection)
    autopilot_service = AutopilotService(connection)
    payload_manager = ExperimentManager(connection)
    task_manager = TaskManager(connection)
    alarm_manager = AlarmManager(connection, remove_alarms_on_init=load_checkpoint)
    orbit_propagator = OrbitPropagator(connection)
    app = Console(
        command_sets=[
            spacecraft_manager,
            autopilot_service,
            payload_manager,
            alarm_manager,
            orbit_propagator,
        ]
    )

    app.cmdloop()

    input("Simulation complete. Press any key to quit...")

    connection.close()
