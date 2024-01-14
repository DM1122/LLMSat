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
from llmsat.components.spacecraft_manager import SpacecraftManager

CHECKPOINT_NAME = "checkpoint"
PROMPTS_FILE_PATH = Path("llmsat/prompts.json")
LLM_NAME = "gpt-4-1106-preview"  # gpt-3.5-turbo-1106
CHECKPOINT_NAME = "checkpoint"


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
    payload_manager = ExperimentManager(connection)
    alarm_manager = AlarmManager(connection)
    app = Console(
        quiet=True,
        command_sets=[
            spacecraft_manager,
            autopilot_service,
            payload_manager,
            alarm_manager,
        ],
    )

    # initialize agent
    KEY = str(config("OPENAI", cast=str))
    llm = ChatOpenAI(openai_api_key=KEY, model=LLM_NAME)

    agent_interface = AgentCMDInterface(app)

    prompts = utils.load_json(PROMPTS_FILE_PATH)
    prompt = prompts["default"]
    system_message = SystemMessage(content=prompt)
    tools = [agent_interface.run]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    result = agent.run(
        prompt
        + "Mission objective from ground control: Set alarms to tell you once you've reached apoapsis"
        + app.get_output()
    )
    print(result)

    input("Simulation complete. Press any key to quit...")

    connection.close()
