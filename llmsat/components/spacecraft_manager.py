"""SpacecraftManager class."""

from datetime import datetime, timedelta
from enum import Enum
from typing import List
import pandas as pd
from cmd2 import CommandSet, with_default_category
from pydantic import BaseModel

from llmsat import utils


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
    RESOURCE_CONVERTER = "resource_converter"
    RESOURCE_HARVESTER = "resource_harvester"
    ROBOTIC_CONTROLLER = "robotic_controller"
    ROBOTIC_HINGE = "robotic_hinge"
    ROBOTIC_PISTON = "robotic_piston"
    ROBOTIC_ROTATION = "robotic_rotation"
    ROBOTIC_ROTOR = "robotic_rotor"
    SENSOR = "sensor"
    SOLAR_PANEL = "solar_panel"
    WHEEL = "wheel"


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


@with_default_category("SpacecraftManager")
class SpacecraftManager(CommandSet):
    """Functions for managing spacecraft systems."""

    def __init__(self, krpc_connection):
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel
        self.spacecraft_description = "An advanced satellite designed to conduct autonomous interplanetary exploration leveraging a Large Language Model-based agentic controller."

        self._assign_ids_to_parts()

    def do_get_spacecraft_properties(self, statement):
        """Get information about the spacecraft"""
        output = self.get_spacecraft_properties()

        self._cmd.poutput(f"Spacecraft properties:\n{output.model_dump_json(indent=4)}")

    def get_spacecraft_properties(self) -> SpacecraftProperties:
        """Get information about the spacecraft"""
        properties = SpacecraftProperties(
            name=self.vessel.name,
            description=self.spacecraft_description,
            type=str(self.vessel.type),
            situation=str(self.vessel.situation),
            met=self.vessel.met,
            biome=self.vessel.biome,
            mass=self.vessel.mass,
            dry_mass=self.vessel.dry_mass,
        )

        return properties

    def do_get_parts_tree(self, statement):
        """Get a tree of all spacecraft parts."""
        output = self.get_parts_tree()

        self._cmd.poutput(output.model_dump_json(indent=4))

    def get_parts_tree(self) -> Part:
        """Get a tree of all spacecraft parts."""

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
                type=self._determine_part_type(krpc_part),
                attachment=attach_mode,
                mass=krpc_part.mass,
                temperature=krpc_part.temperature,
                max_temperature=krpc_part.max_temperature,
                children=[construct_part_tree(child) for child in krpc_part.children],
            )
            return part

        # Start with the root part of the vessel
        root_part = self.vessel.parts.root
        tree = construct_part_tree(root_part)

        return tree

    def do_get_met(self, _):
        """Get the mission elapsed time"""
        met = self.get_met()

        self._cmd.poutput(str(met))

    def get_met(self) -> utils.MET:
        """Gets the current mission elapsed time."""
        met = utils.MET(self.vessel.met)

        return met

    def do_get_ut(self, _):
        """Get the current universal time"""

        time = utils.get_ut(self.connection)

        self._cmd.poutput(time.isoformat())

    def _assign_ids_to_parts(self):
        """Recursively assigns tags to the parts in a tree, starting from the root part."""

        def assign_tag(part: Part, tag: int) -> int:
            part.tag = f"{tag:03}"
            next_tag = tag + 1
            for child in part.children:
                next_tag = assign_tag(child, next_tag)
            return next_tag

        assign_tag(self.vessel.parts.root, tag=0)

    def do_get_resources(self, statement):
        resources = self.get_resources()

        self._cmd.poutput(resources.to_string())

    def get_resources(self) -> pd.DataFrame:
        resources = self.vessel.resources.all
        data = []

        for resource in resources:
            resource_data = {
                "name": resource.name,
                "part": resource.part,
                "amount": resource.amount,
                "max": resource.max,
                "density": resource.density,
                "flow_mode": resource.flow_mode,
                "enabled": resource.enabled,
            }
            data.append(resource_data)

        return pd.DataFrame(data)

    @staticmethod
    def _determine_part_type(krpc_part) -> PartType:
        """
        Dynamically determines the PartType of a given krpc part.
        """
        for part_type in PartType:
            attribute_name = part_type.value
            if (
                hasattr(krpc_part, attribute_name)
                and getattr(krpc_part, attribute_name) is not None
            ):
                return part_type

        return PartType.NONE
