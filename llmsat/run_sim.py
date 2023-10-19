import krpc
import os
import subprocess
from pathlib import Path
from decouple import config
from llmsat.components.obc import OBC
from llmsat.components.comms import Comms
from llmsat.components.payload import PayloadManager
from langchain.llms import OpenAI
from decouple import config
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.tools import tool
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

CHECKPOINT_NAME = "checkpoint"


def is_ksp_running():
    try:
        # List processes and grep for KSP
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8")
        return "KSP" in output
    except:
        return False


def launch_ksp(path: Path):
    subprocess.Popen([path], cwd=os.path.dirname(path))


def load_checkpoint(name: str, space_center):
    """Load the given game save state"""
    try:
        space_center.load(name)
    except ValueError as e:
        raise ValueError(
            f"No checkpoint named '{name}.sfs' was found. Please create one"
        )


if __name__ == "__main__":
    if not is_ksp_running():
        ksp_path = Path(str(config("KSP_PATH")))
        print(f"Launching KSP from '{ksp_path}'...")
        launch_ksp(path=ksp_path)

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    connection = krpc.connect(name="Simulator")
    print(f"Loading '{CHECKPOINT_NAME}.sfs' checkpoint...")
    # load_checkpoint(name=CHECKPOINT_NAME, space_center=connection.space_center)

    science = connection.space_center.science
    print(science)

    vessel = connection.space_center.active_vessel
    # obc = OBC(vessel=vessel)
    # comms = Comms(vessel=vessel)
    payload = PayloadManager(vessel=vessel)

    # initialize agent
    KEY = str(config("OPENAI", cast=str))
    llm = OpenAI(openai_api_key=KEY)
    print(llm)

    system_message = SystemMessage(
        content=f"""You are LLMSat-1. You are a Large Language Model-controlled satellite designed to conduct scientific expeditions around the moon. Your mission begins now. You must take every precaution to survive and complete the mission."""
    )
    tools = [payload.get_experiments]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    result = agent.run("What is your name")
    print(result)

    input("Simulation complete. Press any key to quit...")
    # connection.close()
