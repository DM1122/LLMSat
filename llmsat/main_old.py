"""Main script"""

from agi.stk12.stkengine import STKEngine
from decouple import config
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools import tool


@tool
def get_orbit_state() -> dict:
    """Reads the current orbital state vector from the ADCS module"""

    state = {
        "position [km]": {"x": 6789.0, "y": 1234.0, "z": 5678.0},
        "velocity [km/s]": {"vx": 7.89, "vy": 1.23, "vz": 5.67},
    }

    return state


@tool
def get_spacecraft_state(x: str) -> dict:
    """
    Get the state variables of the spacecraft from its subsystems
    """

    # OBC state
    obc_state = {
        "cpu_load": 55.2,  # percentage
        "ram_usage": 320,  # MB
        "uptime": 15000,  # seconds (represents a bit over 4 hours)
    }

    # EPS state
    eps_state = {
        "battery_level": 78.5,  # percentage
        "solar_panel_voltage": 28.7,  # volts
        "current_consumption": 3.2,  # amperes
    }

    # RF state
    rf_state = {
        "last_received_signal_strength": -110,  # dBm
        "last_transmitted_signal_strength": -85,  # dBm
        "frequency": 437.5,  # MHz (common UHF frequency for CubeSats)
    }

    # ADCS state
    adcs_state = {
        "current_attitude": [1, 0, 0, 0],  # quaternion (representing no rotation)
        "angular_velocity": [0.01, 0.02, 0.03],  # rad/s
        "magnetic_field_strength": [0.2, 0.1, 0.3],  # gauss
    }

    return {
        "obc": obc_state,
        "eps": eps_state,
        "rf": rf_state,
        "adcs": adcs_state,
    }


if __name__ == "__main__":
    KEY = str(config("OPENAI", cast=str))

    llm = OpenAI(openai_api_key=KEY)
    print(llm)
    # stk = STKEngine.StartApplication(noGraphics=True)
    # print(stk.Version)

    system_message = SystemMessage(
        content=f"""You are LLMSat-1. You are a satellite designed to image dust storms on Mars. 
        You are one of ten. Your mission begins now. You must take every precaution to survive and complete the mission."""
    )
    tools = [get_spacecraft_state, get_orbit_state]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": system_message},
    )
    agent.run("What is your name")
