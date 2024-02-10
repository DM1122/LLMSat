"""Autopilot service for orbital maneuvering."""

import json
from string import Template
from typing import List

from cmd2 import CommandSet, with_argparser, with_default_category

from llmsat.libs import utils
from llmsat.libs.krpc_types import Node, Orbit


@with_default_category("AutopilotService")
class AutopilotService(CommandSet):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AutopilotService, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        """Autopilot class."""
        if AutopilotService._initialized:
            return
        super().__init__()

        self.connection = krpc_connection
        self.pilot = self.connection.mech_jeb
        self.vessel = self.connection.space_center.active_vessel

        AutopilotService._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return AutopilotService()._cmd

    operation_apoapsis_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        # epilog=utils.format_return_obj_str(obj=Node, template=Template("List[$obj]")),
    )
    operation_apoapsis_parser.add_argument(
        "--new_apoapsis",
        type=float,
        required=True,
        help="The new apoapsis altitude [m]",
    )

    @with_argparser(operation_apoapsis_parser)
    def do_operation_apoapsis(self, args):
        """Create a maneuver to set a new apoapsis"""

        try:
            nodes = self.operation_apoapsis(args.new_apoapsis)
        except ValueError as e:
            self._cmd.perror(f"Error: {e}")
            return

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def operation_apoapsis(self, new_apoapsis: float) -> List[Node]:
        """Create a maneuver to set a new apoapsis"""

        planner = self.pilot.maneuver_planner.operation_apoapsis

        planner.new_apoapsis = new_apoapsis

        try:
            node_objs = planner.make_nodes()
        except Exception as e:  # catch OperationException
            line = str(e).split("\n", 1)[
                0
            ]  # Split the message at the first newline and take the first part
            raise ValueError(line)

        nodes = [Node(node_obj) for node_obj in node_objs]

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    operation_periapsis_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        # epilog=utils.format_return_obj_str(obj=Node, template=Template("List[$obj]")),
    )
    operation_periapsis_parser.add_argument(
        "--new_periapsis",
        type=float,
        required=True,
        help="The new apoapsis altitude [m]",
    )

    @with_argparser(operation_periapsis_parser)
    def do_operation_periapsis(self, args):
        """Create a maneuver to set a new periapsis"""

        try:
            nodes = self.operation_periapsis(args.new_periapsis)
        except ValueError as e:
            self._cmd.perror(f"Error: {e}")
            return

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def operation_periapsis(self, new_periapsis: float) -> List[Node]:
        """Create a maneuver to set a new periapsis"""

        planner = self.pilot.maneuver_planner.operation_periapsis

        planner.new_periapsis = new_periapsis

        try:
            node_objs = planner.make_nodes()
        except Exception as e:  # catch OperationException
            line = str(e).split("\n", 1)[
                0
            ]  # Split the message at the first newline and take the first part
            raise ValueError(line)

        nodes = [Node(node_obj) for node_obj in node_objs]

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    operation_inclination_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        # epilog=utils.format_return_obj_str(obj=Node, template=Template("List[$obj]")),
    )
    operation_inclination_parser.add_argument(
        "--new_inclination",
        type=float,
        required=True,
        help="The new inclination [deg]",
    )

    @with_argparser(operation_inclination_parser)
    def do_operation_inclination(self, args):
        """Create a maneuver to change inclination"""

        try:
            nodes = self.operation_inclination(args.new_inclination)
        except ValueError as e:
            self._cmd.perror(f"Error: {e}")
            return

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def operation_inclination(self, new_inclination: float) -> List[Node]:
        """Create a maneuver to change inclination"""

        planner = self.pilot.maneuver_planner.operation_inclination

        planner.new_inclination = new_inclination

        try:
            node_objs = planner.make_nodes()
        except Exception as e:  # catch OperationException
            line = str(e).split("\n", 1)[
                0
            ]  # Split the message at the first newline and take the first part
            raise ValueError(line)

        nodes = [Node(node_obj) for node_obj in node_objs]

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    operation_circularize_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        # epilog=utils.format_return_obj_str(obj=Node, template=Template("List[$obj]")),
    )

    @with_argparser(operation_circularize_parser)
    def do_operation_circularize(self, args):
        """Creates a manevuer to match your apoapsis to periapsis"""

        try:
            nodes = self.operation_circularize()
        except ValueError as e:
            self._cmd.perror(f"Error: {e}")
            return

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def operation_circularize(self) -> List[Node]:
        """Create a maneuver to change circularize"""

        planner = self.pilot.maneuver_planner.operation_circularize

        try:
            node_objs = planner.make_nodes()
        except Exception as e:  # catch OperationException
            line = str(e).split("\n", 1)[
                0
            ]  # Split the message at the first newline and take the first part
            raise ValueError(line)

        nodes = [Node(node_obj) for node_obj in node_objs]

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    def do_execute_maneuver_nodes(self, args):
        """Execute all planned maneuver nodes"""

        self._cmd.poutput("Executing planned maneuver nodes")
        new_orbit = self.execute_maneuver_nodes()

        # self._cmd.poutput(
        #     f"Maneuver(s) executed successfully! New orbit:\n{new_orbit.model_dump_json(indent=4)}"
        # )

    def execute_maneuver_nodes(self) -> Orbit:
        """Execute all planned maneuver nodes"""
        executor = self.pilot.node_executor
        executor.autowarp = True
        executor.execute_all_nodes()

        # with self.connection.stream(getattr, executor, "enabled") as enabled:
        #     enabled.rate = (
        #         1  # we don't need a high throughput rate, 1 second is more than enough
        #     )
        #     with enabled.condition:
        #         while enabled():
        #             enabled.wait()

        # return self.get_orbit()

    def do_get_nodes(self, _=None):
        """Returns a list of all existing maneuver nodes, ordered by time from first to last."""

        nodes = self.get_nodes()

        self._cmd.poutput(nodes)

    def get_nodes(self) -> List[Node]:
        """Returns a list of all existing maneuver nodes, ordered by time from first to last."""

        node_objs = self.vessel.control.nodes
        nodes = [Node(node_obj) for node_obj in node_objs]

        return nodes

    def do_remove_nodes(self, _=None):
        """Remove all maneuver nodes"""

        node_count = len(self.get_nodes)

        self.remove_nodes()

        self._cmd.poutput(f"Removed {node_count} nodes")

    def remove_nodes(self):
        """Remove all maneuver nodes"""
        self.vessel.control.remove_nodes()

    # def do_launch(self, args):
    #     """Launch into orbit"""

    #     self.launch()

    #     self._cmd.poutput()

    # def launch(self):
    #     """Launch into orbit"""
    #     pilot_ascent = self.pilot.ascent_autopilot

    #     pilot_ascent.desired_orbit_altitude = 100000
    #     pilot_ascent.desired_inclination = 6
    #     pilot_ascent.autostage = True
    #     pilot_ascent.enabled = True

    # def do_land(self, _=None):
    #     """Land"""

    #     output = self.land()

    #     self._cmd.poutput(output)

    # def land(self):
    #     """land"""
    #     pilot_landing = self.pilot.landing_autopilot

    #     pilot_landing.deploy_gears = True
    #     pilot_landing.rcs_adjustment = True
    #     pilot_landing.touchdown_speed = 0.6  # m/s
    #     pilot_landing.land_at_position_target()

    #     # pilot_landing.enabled = True

    #     return pilot_landing.status
