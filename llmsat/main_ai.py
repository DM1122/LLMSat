"""Runs simulation loop"""

import os
from pathlib import Path

import krpc
import prompt
import json
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI

from llmsat.components.alarm_manager import AlarmManager
from llmsat.components.autpilot import AutopilotService
from llmsat.components.console import AgentCMDInterface, Console
from llmsat.components.experiment_manager import ExperimentManager
from llmsat.components.spacecraft_manager import SpacecraftManager
from llmsat.libs import utils

CONFIG_PATH = "llmsat/app_config.json"


if __name__ == "__main__":
    # setup langsmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_API_KEY"] = config("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_PROJECT"] = "llmsat"

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
    llm = ChatOpenAI(openai_api_key=KEY, model=app_config.model)

    agent_interface = AgentCMDInterface(app)

    tools = [agent_interface.run]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
            "prefix": prompt.PREFIX,
            "format_instructions": prompt.FORMAT_INSTRUCTIONS,
            "suffix": prompt.SUFFIX,
        },
    )
    result = agent.run(app.get_output())
    print(result)

    input("Simulation complete. Press any key to quit...")

    connection.close()
