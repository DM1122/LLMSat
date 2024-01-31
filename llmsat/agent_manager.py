"""Agent Manager"""
import asyncio
import json
import os
from pathlib import Path

import prompt
import zmq
import zmq.asyncio
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from llmsat.libs import utils

CONFIG_PATH = Path("llmsat/app_config.json")


class AgentManager:
    """Manage state and execution of agent."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AgentManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self, openai_key: str, langchain_key: str, model: str, port: int
    ) -> None:
        # setup singleton to enable class methods as langchain tools
        if AgentManager._initialized:
            return
        AgentManager._initialized = True

        # setup langsmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = langchain_key
        os.environ["LANGCHAIN_PROJECT"] = "llmsat"

        # setup agent
        llm = ChatOpenAI(openai_api_key=openai_key, model=model)
        tools = [self.run]
        self.agent: AgentExecutor = initialize_agent(
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

        # setup connection
        context = zmq.asyncio.Context()
        self.connection = context.socket(zmq.PAIR)
        self.connection.connect(f"tcp://localhost:{port}")
        asyncio.create_task(self.receive_messages())

        print("Agent manager initialized")

    @staticmethod
    def _get_instance():
        """Get the current instance of the class"""
        return AgentManager(None, None, None)

    @staticmethod
    @tool()
    def run(input: str):
        """Write a command to the console"""
        manager = AgentManager._get_instance()
        manager.connection.send_message(input)

        response = manager.connection.recv_string()

        return response

    def send_message(self, message: str) -> str:
        """Send a message to the server"""

        self.connection.send_message(message)
        response = self.connection.recv_string()
        return response

    async def receive_messages(self):
        """Receive messages from the app asynchronously."""
        while True:
            print("Checking messages")
            message = await self.connection.recv_string()
            print(f"Received from app: {message}")


async def main():
    LANGCHAIN_KEY = config("LANGCHAIN_API_KEY")
    OPENAI_KEY = str(config("OPENAI", cast=str))

    with open(CONFIG_PATH, "r") as file:
        app_config_data = json.load(file)
        app_config = utils.AppConfig(**app_config_data)

    agent_manager = AgentManager(
        openai_key=OPENAI_KEY,
        langchain_key=LANGCHAIN_KEY,
        model=app_config.model,
        port=app_config.port,
    )
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
    # LANGCHAIN_KEY = config("LANGCHAIN_API_KEY")
    # OPENAI_KEY = str(config("OPENAI", cast=str))

    # with open(CONFIG_PATH, "r") as file:
    #     app_config_data = json.load(file)
    #     app_config = utils.AppConfig(**app_config_data)

    # AgentManager(
    #     openai_key=OPENAI_KEY, langchain_key=LANGCHAIN_KEY, model=app_config.model
    # )
