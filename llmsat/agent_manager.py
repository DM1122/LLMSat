"""Agent Manager"""
import json
import os
from pathlib import Path
import threading
import prompt
import zmq
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import queue
import time

from llmsat.libs import utils

CONFIG_PATH = Path("llmsat/app_config.json")


class AgentManager:
    """Manage state and execution of agent.

    The agent interfaces with the console app server.
    """

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
        self.message_queue = queue.Queue()
        self.connected = False
        context = zmq.Context()
        self.connection = context.socket(zmq.PAIR)
        self.connection.connect(f"tcp://localhost:{port}")
        receive_thread = threading.Thread(
            name="agent-receive-message", target=self.receive_message, daemon=True
        )
        receive_thread.start()

        print("Connecting to console session")
        connect_message = utils.Message(type=utils.MessageType.CONNECT)
        self.send_message(connect_message)
        self.connected = True

        print("Agent manager initialized")
        self.main_loop()

    @staticmethod
    def _get_instance():
        """Get the current instance of the class"""
        return AgentManager(None, None, None, None)

    @staticmethod
    @tool()
    def run(input: str):
        """Write a command to the console"""
        manager = AgentManager._get_instance()
        message = utils.Message(type=utils.MessageType.COMMAND, data=input)
        manager.send_message(message)

        response = manager.message_queue.get(block=True)

        return response

    def send_message(self, message: utils.Message):
        """Send a message to the server"""
        self.connection.send_pyobj(message)

    def receive_message(self):
        """Receive messages from the console asynchronously and add them to the queue."""
        while True:
            message = self.connection.recv_string()
            self.message_queue.put(message)

    def main_loop(self):
        while True:
            if not self.connected:  # not the first connection
                alert = self.message_queue.get(block=True)
                print("Connecting to console session")
                connect_message = utils.Message(type=utils.MessageType.CONNECT)
                self.send_message(connect_message)
                self.connected = True

                response = self.message_queue.get(block=True)
                result = self.agent.run(response + "\n" + alert)
                print(result)

                disconnect_message = utils.Message(type=utils.MessageType.DISCONNECT)
                self.send_message(disconnect_message)
                self.connected = False

            else:  # first connection
                response = self.message_queue.get(block=True)
                result = self.agent.run(response)
                print(result)

                disconnect_message = utils.Message(type=utils.MessageType.DISCONNECT)
                self.send_message(disconnect_message)
                self.connected = False


if __name__ == "__main__":
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
