from pathlib import Path

from langchain.tools import tool
from langchain.tools.base import ToolException
from pydantic import BaseModel
import json


class SpacecraftProperties(BaseModel):
    """Basic properties of the spacecraft"""

    name: str
    description: str
    type: str
    situation: str
    met: float
    biome: str
    mass: float
    dry_mass: float

class OBC:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OBC, cls).__new__(cls)
        return cls._instance

    def __init__(self, vessel=None):
        if OBC._initialized:
            return
        self.vessel = vessel
        OBC._initialized = True

    @staticmethod
    def _get_instance():
        instance = OBC()
        if instance.vessel is None:
            raise ValueError(
                "OBC must be initialized with a vessel before calling its methods."
            )
        return OBC()
    
    @staticmethod
    @tool(handle_tool_error=True)
    def get_experiments() -> str:
        """Get information about all available experiments"""
        vessel = OBC._get_instance().vessel

        properties = SpacecraftProperties(
            name=vessel.name,
            description="A description",
            type=str(vessel.type),
            situation=str(vessel.situation),
            met=vessel.met,
            biome=vessel.biome,
            mass=vessel.mass,
            dry_mass=vessel.dry_mass,
        )

        return json.dumps(properties, indent=4, default=lambda o: o.dict())
    
    @staticmethod
    @tool(handle_tool_error=True)
    def get_parts_list() -> str:
        """Get a tree list of all spacecraft components"""
        vessel = OBC._get_instance().vessel

        return vessel.parts.all
