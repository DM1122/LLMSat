"""Runs simulation loop"""

from pathlib import Path

import krpc
import utils
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

from llmsat.components import OBC, PayloadManager

CHECKPOINT_NAME = "checkpoint"
PROMPTS_FILE_PATH = Path("llmsat/prompts.json")
LLM_NAME = "gpt-3.5-turbo-0613"  # "gpt-4-0613"


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

    science = connection.space_center.science
    print(science)

    vessel = connection.space_center.active_vessel
    payload = PayloadManager(vessel=vessel)

    # initialize agent
    KEY = str(config("OPENAI", cast=str))
    llm = ChatOpenAI(openai_api_key=KEY, model=LLM_NAME)
    print(llm)

    prompts = utils.load_json(PROMPTS_FILE_PATH)
    prompt = prompts["default"]
    system_message = SystemMessage(content=prompt)
    tools = [
        OBC.get_spacecraft_properties,
        # OBC.get_parts_list,
        # PayloadManager.get_experiments,
        # PayloadManager.run_experiment,
    ]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    result = agent.run("Run the thermal experiment")
    print(result)

    input("Simulation complete. Press any key to quit...")

    connection.close()
