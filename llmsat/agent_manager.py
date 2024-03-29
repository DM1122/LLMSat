"""Agent Manager"""

import json
import os
import queue
import threading
from pathlib import Path
import asyncio
import prompt
import zmq
from decouple import config
from langchain.agents import AgentType, initialize_agent
from langchain.agents.agent import AgentExecutor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

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
        self,
        openai_key: str,
        langchain_key: str,
        model: str,
        temperature: float,
        port: int,
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

        # threads
        self.streaming_thread = None
        self.receive_thread = threading.Thread(
            name="agent-receive-message", target=self.receive_message, daemon=True
        )

        # setup agent
        llm = ChatOpenAI(
            openai_api_key=openai_key,
            model=model,
            temperature=temperature,
            streaming=True,
        )
        tools = [self.run, self.sleep]

        memory = ConversationBufferWindowMemory(k=2, return_messages=True)
        # history = MessagesPlaceholder(variable_name="history")
        self.agent: AgentExecutor = initialize_agent(
            tools=tools,
            llm=llm,
            memory=memory,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            agent_kwargs={
                "prefix": prompt.PREFIX,
                "format_instructions": prompt.FORMAT_INSTRUCTIONS,
                "suffix": prompt.SUFFIX,
                # "max_execution_time": 9999,
                # "history": [history],
                # "memory_prompts": [history],
                # "input_variables": ["input", "agent_scratchpad", "history"],
            },
            max_iterations=None,
        )

        # setup connection to console
        self.message_queue = queue.Queue()
        self.connected = False
        context = zmq.Context()
        self.connection = context.socket(zmq.PAIR)
        self.connection.connect(f"tcp://localhost:{port}")

        # start message receiver
        self.receive_thread.start()

        print("Connecting to console session")
        connect_message = utils.Message(type=utils.MessageType.CONNECT)
        self.send_message(connect_message)
        self.connected = True

        print("Agent manager initialized")
        self.main_loop()

    @staticmethod
    def _get_instance():
        """Get the current instance of the class"""
        return AgentManager(None, None, None, None, None)

    @staticmethod
    @tool()
    def run(input: str) -> str:
        """Write a command to the console"""
        manager = AgentManager._get_instance()
        message = utils.Message(type=utils.MessageType.COMMAND, data=input)
        manager.send_message(message)

        # get all messages in the queue at once (TODO: temporary until streaming works)
        response: str = manager.message_queue.get(block=True, timeout=5)
        # continue extracting messages from the queue if still not empty
        # while not manager.message_queue.empty():
        #     try:
        #         response += manager.message_queue.get(block=False)
        #     except queue.Empty:
        #         break  # Break out of the loop if the queue is empty

        return response

    @staticmethod
    @tool()
    def sleep() -> str:
        """Sleep until the next notification is received"""
        manager = AgentManager._get_instance()
        response = manager.message_queue.get(block=True)

        return response

    def start_streaming_thread(self, input_str: str):
        if self.streaming_thread is not None:
            self.streaming_thread.join()  # Ensure previous thread is finished

        self.streaming_thread = threading.Thread(
            target=self.stream_agent_response, args=[str(input_str)]
        )
        self.streaming_thread.start()

    def stream_agent_response(self, input_str: str):
        async def async_stream():
            async for event in self.agent.astream_events(
                {"input": input_str},
                version="v1",
            ):
                kind = event["event"]

                # Print tokens as they are generated by the agent
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        pass  # print(content, end="")

                # TODO: if an message is recieved in the queue it is an alert message, so interrupt the stream and pass the alert to the LLM agent so it can handle it
                # https://www.reddit.com/r/LangChain/comments/13q1p5c/how_do_you_stop_streaming_when_using_chatgpt_api/

        asyncio.run(async_stream())

    def send_message(self, message: utils.Message):
        """Send a message to the server"""
        self.connection.send_pyobj(message)

    def receive_message(self):
        """Receive messages from the console asynchronously and add them to the queue."""
        while True:
            message = self.connection.recv_string()
            self.message_queue.put(message)

    def main_loop(self):
        # while True:
        #     if not self.connected:  # not the first connection
        #         alert = self.message_queue.get(block=True)
        #         print("Connecting to console session")
        #         connect_message = utils.Message(type=utils.MessageType.CONNECT)
        #         self.send_message(connect_message)
        #         self.connected = True

        #         response = self.message_queue.get(block=True)
        #         result = self.start_streaming_thread(response + "\n" + alert)

        #         self.streaming_thread.join()
        #         disconnect_message = utils.Message(type=utils.MessageType.DISCONNECT)
        #         self.send_message(disconnect_message)
        #         self.connected = False

        #     else:  # first connection
        response = self.message_queue.get(block=True)
        result = self.start_streaming_thread(response)
        print(result)
        self.streaming_thread.join()

        disconnect_message = utils.Message(type=utils.MessageType.DISCONNECT)
        self.send_message(disconnect_message)
        self.connected = False


if __name__ == "__main__":
    LANGCHAIN_KEY = config("LANGCHAIN_API_KEY")
    OPENAI_KEY = str(config("OPENAI", cast=str))

    with open(CONFIG_PATH, "r") as file:
        app_config_data = json.load(file)
        app_config = utils.AppConfig(**app_config_data)

    print(app_config.port)
    agent_manager = AgentManager(
        openai_key=OPENAI_KEY,
        langchain_key=LANGCHAIN_KEY,
        model=app_config.model,
        temperature=app_config.temperature,
        port=app_config.port,
    )
