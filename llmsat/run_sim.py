from pathlib import Path

import krpc
import utils
from decouple import config
from langchain.agents import AgentType, initialize_agent, load_tools, react
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools import Tool, tool

from llmsat.components.comms import Comms
from llmsat.components.obc import OBC
from llmsat.components.payload import PayloadManager

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

    science = connection.space_center.science
    print(science)

    vessel = connection.space_center.active_vessel
    payload = PayloadManager(vessel=vessel)

    # initialize agent
    KEY = str(config("OPENAI", cast=str))
    llm = ChatOpenAI(openai_api_key=KEY, model="gpt-4-0613")
    print(llm)

    system_message = SystemMessage(
        content=f"""You are LLMSat-1. You are a Large Language Model-controlled satellite designed to conduct scientific expeditions around the moon. Your mission begins now. You must take every precaution to survive and complete the mission."""
    )
    tools = [PayloadManager.get_experiments, PayloadManager.run_experiment]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    result = agent.run("Run a temperature experiment in orbit around the moon")
    print(result)

    input("Simulation complete. Press any key to quit...")

    connection.close()
