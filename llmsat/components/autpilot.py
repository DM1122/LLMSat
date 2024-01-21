"""Autopilot class."""
import json
from typing import List

from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat.libs import utils


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

    plan_apoapsis_maneuver_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        epilog=f"Returns:\nList[{Node.model_json_schema()['title']}]: {json.dumps(Node.model_json_schema()['properties'], indent=4)}",
    )
    plan_apoapsis_maneuver_parser.add_argument(
        "--new_apoapsis",
        type=float,
        required=True,
        help="The new apoapsis altitude [km]",
    )

    @with_argparser(plan_apoapsis_maneuver_parser)
    def do_apoapsis(self, args):
        """Plan an apoapsis maneuver"""

        nodes = self.apoapsis(args.new_apoapsis)

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def apoapsis(self, new_apoapsis: float) -> List[Node]:
        """Plan an apoapsis maneuver"""

        planner = self.pilot.maneuver_planner.operation_apoapsis

        planner.new_apoapsis = new_apoapsis * 1000
        # planner.time_selector.time_reference.computed
        node_objs = planner.make_nodes()
        nodes = []
        for node_obj in node_objs:
            nodes.append()

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    def do_execute_maneuver_nodes(self, args):
        """Execute all planned maneuver nodes"""

        self._cmd.poutput("Executing planned maneuver nodes")
        new_orbit = self.execute_maneuver_nodes()

        self._cmd.poutput(
            f"Maneuver(s) executed successfully! New orbit:\n{new_orbit.model_dump_json(indent=4)}"
        )

    def execute_maneuver_nodes(self) -> utils.Orbit:
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

        return self.get_orbit()

    def get_orbit(self) -> utils.Orbit:
        """Gets the current orbit"""

        obj = self.vessel.orbit
        orbit = utils.cast_krpc_orbit(obj)

        return orbit

    def do_launch(self, args):
        """Launch into orbit"""

        self.launch()

        self._cmd.poutput()

    def launch(self):
        """Launch into orbit"""
        pilot_ascent = self.pilot.ascent_autopilot

        pilot_ascent.desired_orbit_altitude = 100000
        pilot_ascent.desired_inclination = 6
        pilot_ascent.autostage = True
        pilot_ascent.enabled = True

    def do_land(self, _=None):
        """Land"""

        output = self.land()

        self._cmd.poutput(output)

    def land(self):
        """land"""
        pilot_landing = self.pilot.landing_autopilot

        pilot_landing.deploy_gears = True
        pilot_landing.rcs_adjustment = True
        pilot_landing.touchdown_speed = 0.6  # m/s
        pilot_landing.land_at_position_target()

        # pilot_landing.enabled = True

        return pilot_landing.status
