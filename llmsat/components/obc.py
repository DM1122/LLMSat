import json
from enum import Enum
from pathlib import Path
from typing import List, Optional
import inspect
import krpc
from langchain.tools import tool
from langchain.tools.base import ToolException
from pydantic import BaseModel


def custom_tool(func):
    # Retrieve the signature and docstring
    signature = inspect.signature(func)
    docstring = func.__doc__ or ""
    func_info = f"{func.__name__}{signature} - {docstring.strip()}"

    # Create a wrapper that returns the formatted string
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.is_exposed = True
    wrapper.info = func_info
    return wrapper


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


class AttachmentMode(Enum):
    RADIAL = "radial"
    AXIAL = "axial"


class PartType(Enum):
    NONE = "none"
    ANTENNA = "antenna"
    CARGO_BAY = "cargo_bay"
    CONTROL_SURFACE = "control_surface"
    DECOUPLER = "decoupler"
    DOCKING_PORT = "docking_port"
    ENGINE = "engine"
    EXPERIMENT = "experiment"
    EXPERIMENTS = "experiements"
    FAIRING = "fairing"
    INTAKE = "intake"
    LEG = "leg"
    LAUNCH_CLAMP = "launch_clamp"
    LIGHT = "light"
    PARACHUTE = "parachute"
    RADIATOR = "radiator"
    RESOURCE_DRAIN = "resource_drain"
    RCS = "rcs"
    REACTION_WHEEL = "reaction_wheel"
    RESOURCe_CONVERTER = "resource_converter"
    RESOURCE_HARVESTER = "resource_harvester"
    ROBOTIC_CONTROLLER = "robotic_controller"
    ROBOTIC_HINGE = "robotic_hinge"
    ROBOTIC_PISTON = "robotic_piston"
    ROBOTIC_ROTATION = "robotic_rotation"
    ROBOTIC_ROTOR = "robotic_rotor"
    SENSOR = "sensor"
    SOLAR_PANEL = "solar_panel"
    WHEEL = "wheel"


class Part(BaseModel):
    id: str
    name: str
    title: str
    type: PartType
    mass: float
    temperature: float
    max_temperature: float
    attachment: AttachmentMode
    children: List["Part"]


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

    @custom_tool
    def get_spacecraft_properties(self, a: int, b: float, c) -> str:
        """Get information about the vessel"""
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
    def determine_part_type(krpc_part) -> PartType:
        """
        Dynamically determines the PartType of a given krpc part.
        """
        # Iterate over the PartType enum members
        for part_type in PartType:
            # Convert the enum member to the corresponding krpc attribute
            # Assumes that the enum value is the same as the krpc attribute name
            attribute_name = part_type.value
            # Check if the attribute exists and is not None
            if (
                hasattr(krpc_part, attribute_name)
                and getattr(krpc_part, attribute_name) is not None
            ):
                return part_type

        return PartType.NONE

    def assign_ids_to_parts(self):
        """Recursively assigns tags to the parts in a tree, starting from the root part."""

        def assign_tag(part: Part, tag: int) -> int:
            # Format the tag as a three-digit string
            part.tag = f"{tag:03}"
            next_tag = tag + 1  # Increment the tag for the next part
            for child in part.children:
                next_tag = assign_tag(
                    child, next_tag
                )  # Recursively assign tags to children
            return next_tag  # Return the next tag to be used

        assign_tag(self.vessel.parts.root, tag=0)

    @staticmethod
    def get_parts_tree() -> str:
        """Get a tree of all spacecraft parts."""
        vessel = OBC._get_instance().vessel

        def construct_part_tree(krpc_part) -> Part:
            """
            Recursively constructs a tree of parts from the given KRPC part.
            """
            if krpc_part.axially_attached:
                attach_mode = AttachmentMode.AXIAL
            else:
                attach_mode = AttachmentMode.RADIAL

            part = Part(
                id=krpc_part.tag,
                name=krpc_part.name,
                title=krpc_part.title,
                type=OBC.determine_part_type(krpc_part),
                attachment=attach_mode,
                mass=krpc_part.mass,
                temperature=krpc_part.temperature,
                max_temperature=krpc_part.max_temperature,
                children=[construct_part_tree(child) for child in krpc_part.children],
            )
            return part

        # Start with the root part of the vessel
        root_part = vessel.parts.root
        tree = construct_part_tree(root_part)

        return tree.model_dump_json(indent=4)
