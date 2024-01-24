"""SpacecraftManager class."""

from datetime import datetime
from pathlib import Path

import pandas as pd
from cmd2 import CommandSet, with_default_category

from llmsat.libs import utils
from llmsat.libs.krpc_types import Part, PartType, SpacecraftProperties

MISSION_BRIEF = Path("disk/mission.md")


@with_default_category("SpacecraftManager")
class SpacecraftManager(CommandSet):
    """Functions for managing spacecraft systems."""

    def __init__(self, krpc_connection):
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

        self._assign_ids_to_parts()

    def do_get_spacecraft_properties(self, _=None):
        """Get information about the spacecraft"""
        output = self.get_spacecraft_properties()

        self._cmd.poutput(output.model_dump_json(indent=4))

    def get_spacecraft_properties(self) -> SpacecraftProperties:
        """Get information about the spacecraft"""
        properties = SpacecraftProperties(self.vessel)

        return properties

    def do_get_parts_tree(self, _=None):
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

    def do_get_met(self, _=None):
        """Get the mission elapsed time"""
        met = self.get_met()

        self._cmd.poutput(str(met))

    def get_met(self) -> utils.MET:
        """Gets the current mission elapsed time."""
        met = utils.MET(self.vessel.met)

        return met

    def do_get_ut(self, _=None):
        """Get the current universal time"""
        ut = self.get_ut()

        self._cmd.poutput(ut.isoformat())

    def get_ut(self) -> datetime:
        """Get the current universal time"""
        return utils.ksp_ut_to_datetime(self.connection.space_center.ut)

    def _assign_ids_to_parts(self):
        """Recursively assigns tags to the parts in a tree, starting from the root part."""

        def assign_tag(part: Part, tag: int) -> int:
            part.tag = f"{tag:03}"
            next_tag = tag + 1
            for child in part.children:
                next_tag = assign_tag(child, next_tag)
            return next_tag

        assign_tag(self.vessel.parts.root, tag=0)

    def do_get_resources(self, _=None):
        resources = self.get_resources()

        self._cmd.poutput(resources.to_string())

    def get_resources(self) -> pd.DataFrame:
        resources = self.vessel.resources

        data = []
        for name in resources.names:
            resource_data = {
                "name": name,
                "amount": resources.amount(name),
                "max": resources.max(name),
                # "density": resources.density(name),  # TODO: AttributeError: type object 'Resources' has no attribute '_client'
                # "flow_mode": resources.flow_mode(name),
            }
            data.append(resource_data)

        return pd.DataFrame(data)

    def do_read_mission_brief(self, _=None):
        """Read the mission briefing"""
        self._cmd.poutput(self.read_mission_brief())

    def read_mission_brief(self) -> str:
        with open(MISSION_BRIEF, "r") as file:
            text = file.read()
        return text

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
