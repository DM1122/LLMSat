"""Autopilot class."""
import json
from typing import List

from llmsat import utils
from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field


class Node(BaseModel):
    "Represents a maneuver node."

    prograde: float = Field(
        description="The magnitude of the maneuver nodes delta-v in the prograde direction, in meters per second."
    )
    normal: float = Field(
        description="The magnitude of the maneuver nodes delta-v in the normal direction, in meters per second."
    )
    radial: float = Field(
        description="The magnitude of the maneuver nodes delta-v in the radial direction, in meters per second."
    )
    delta_v: float = Field(
        description="The delta-v of the maneuver node, in meters per second. Does not change when executing the maneuver node. See remaining_delta_v."
    )
    remaining_delta_v: float = Field(
        description="Gets the remaining delta-v of the maneuver node, in meters per second. Changes as the node is executed."
    )
    ut: float = Field(
        description="The universal time at which the maneuver will occur, in seconds."
    )
    time_to: float = Field(
        description="The time until the maneuver node will be encountered, in seconds."
    )
    new_orbit: utils.Orbit = Field(
        description="The new orbit to be achieved after execution of the maneuver"
    )


@with_default_category("AutopilotService")
class AutopilotService(CommandSet):
    def __init__(self, krpc_connection):
        """Autopilot class."""
        super().__init__()

        self.connection = krpc_connection
        self.pilot = self.connection.mech_jeb
        self.vessel = self.connection.space_center.active_vessel

    plan_apoapsis_maneuver_parser = Cmd2ArgumentParser(
        epilog=f"Returns:\nList[{Node.model_json_schema()['title']}]: {json.dumps(Node.model_json_schema()['properties'], indent=4)}"
    )
    plan_apoapsis_maneuver_parser.add_argument(
        "--new_apoapsis",
        type=float,
        required=True,
        help="The new apoapsis altitude [km]",
    )

    @with_argparser(plan_apoapsis_maneuver_parser)
    def do_plan_apoapsis_maneuver(self, args):
        """Plan an apoapsis change"""
        plan_apoapsis_parser = Cmd2ArgumentParser()
        plan_apoapsis_parser.add_argument(
            "new_apoapsis", type=float, help="[km] The new apoapsis altitude"
        )

        self._cmd.poutput("Generating maneuver nodes...")

        nodes = self.plan_apoapsis_maneuver(args.new_apoapsis)

        self._cmd.poutput("The following nodes were generated:")
        for node in nodes:
            self._cmd.poutput(node.model_dump_json(indent=4))

    def plan_apoapsis_maneuver(self, new_apoapsis: float) -> List[Node]:
        """Create a maneuver to set a new apoapsis"""

        planner = self.pilot.maneuver_planner.operation_apoapsis

        planner.new_apoapsis = new_apoapsis * 1000
        # planner.time_selector.time_reference.computed
        node_objs = planner.make_nodes()
        nodes = []
        for node_obj in node_objs:
            nodes.append(
                Node(
                    prograde=node_obj.prograde,
                    normal=node_obj.normal,
                    radial=node_obj.radial,
                    delta_v=node_obj.delta_v,
                    remaining_delta_v=node_obj.remaining_delta_v,
                    ut=node_obj.ut,
                    time_to=node_obj.time_to,
                    new_orbit=utils.cast_krpc_orbit(node_obj.orbit),
                )
            )

        warning = planner.error_message
        if warning:
            self._cmd.poutput(warning)

        return nodes

    def do_execute_maneuver(self, args):
        """Execute a planned maneuver nodes"""

        self._cmd.poutput("Executing planned maneuver nodes")
        new_orbit = self.execute_maneuver()

        self._cmd.poutput(
            f"Maneuver(s) executed successfully! New orbit:\n{new_orbit.model_dump_json(indent=4)}"
        )

    def execute_maneuver(self) -> utils.Orbit:
        """Execute a planned maneuver nodes"""
        executor = self.pilot.node_executor
        print("Executor")
        executor.autowarp = True
        print("Autowarp")
        executor.execute_all_nodes()
        print("do the ting")

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
