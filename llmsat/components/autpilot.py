from pathlib import Path

from langchain.tools import tool
from langchain.tools.base import ToolException
from pydantic import BaseModel
import json

class AutopilotService:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AutopilotService, cls).__new__(cls)
        return cls._instance

    def __init__(self, connection=None):
        """
        Args:
            pilot: Mechjeb autpilot instance
        """
        if AutopilotService._initialized:
            return
        
        self.connection = connection
        self.pilot = connection.mech_jeb

        AutopilotService._initialized = True

    @staticmethod
    def _get_instance():
        instance = AutopilotService()
        if instance.connection is None:
            raise ValueError(
                "AutopilotService must be initialized with a connection before calling its methods."
            )
        return AutopilotService()
    
    @staticmethod
    @tool(handle_tool_error=True)
    def plan_apoapsis_maneuver() -> str:
        """Create a maneuver to set a new apoapsis"""
        pilot = AutopilotService._get_instance().pilot

        planner = pilot.maneuver_planner.operation_apoapsis
        planner.make_nodes()

        #check for warnings
        warning = planner.error_message
        if warning:
            print(warning)

        #execute the nodes
        AutopilotService._get_instance().execute_nodes()

    def execute_nodes(self):
        print("Executing maneuver nodes")
        executor = self.pilot.node_executor
        executor.execute_all_nodes()
        
        with self.connection.stream(getattr, executor, "enabled") as enabled:
            enabled.rate = 1 # we don't need a high throughput rate, 1 second is more than enough
            with enabled.condition:
                while enabled():
                    enabled.wait()