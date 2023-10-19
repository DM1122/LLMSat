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

class Test():
    def __init__(self):
        self.x = 0
    
    @tool
    def increment(self, x: str) -> str:
        """Increment the counter by given number"""
        self.x += int(x)
        return str(self.x)
        

print("running")
clss = Test()



# initialize agent
KEY = str(config("OPENAI", cast=str))
llm = OpenAI(openai_api_key=KEY)
print(llm)

system_message = SystemMessage(
    content=f"""You are a calculator"""
)
tools = [clss.increment]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message},
)
result = agent.run("Please increment the counter")
print(result)


    # def _make_with_name(tool_name: str) -> Callable:
    #     def _make_tool(dec_func: Callable) -> BaseTool:
    #         #region MOD
    #         is_bound_method = inspect.ismethod(dec_func)

    #         if is_bound_method:
    #             # Adjust how dec_func is called if it's a bound method
    #             func = lambda *args, **kwargs: dec_func.__func__(dec_func.__self__, *args, **kwargs)
    #         else:
    #             func = dec_func
    #         #endregion

    #         if inspect.iscoroutinefunction(dec_func):