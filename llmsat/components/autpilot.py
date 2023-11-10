"""Autopilot class."""
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from pydantic import BaseModel, Field


class Orbit(BaseModel):
    body: str = Field(description="The celestial body (e.g. planet or moon) around which the object is orbiting.")
    apoapsis: float = Field(description="Gets the apoapsis of the orbit, in meters, from the center of mass of the body being orbited.")
    periapsis: float = Field(description="The periapsis of the orbit, in meters, from the center of mass of the body being orbited.")
    apoapsis_altitude: float = Field(description="The apoapsis of the orbit, in meters, above the sea level of the body being orbited.")
    periapsis_altitude: float = Field(description="The periapsis of the orbit, in meters, above the sea level of the body being orbited.")
    semi_major_axis: float = Field(description="The semi-major axis of the orbit, in meters.")
    semi_minor_axis: float = Field(description="The semi-minor axis of the orbit, in meters.")
    radius: float = Field(description="The current radius of the orbit, in meters. This is the distance between the center of mass of the object in orbit, and the center of mass of the body around which it is orbiting.")
    speed: float = Field(description="The orbital speed of the object in meters per second. This value will change over time if the orbit is elliptical.")
    period: float = Field(description="The orbital period, in seconds.")
    eccentricity: float = Field(description="The eccentricity of the orbit.")
    inclination: float = Field(description="The inclination of the orbit, in radians.")
    longitude_of_ascending_node: float = Field(description="The longitude of the ascending node, in radians.")
    argument_of_periapsis: float = Field(description="The argument of periapsis, in radians.")

class Node(BaseModel):
    "Represents a maneuver node."

    prograde: float = Field(description="The magnitude of the maneuver nodes delta-v in the prograde direction, in meters per second.")
    normal: float = Field(description="The magnitude of the maneuver nodes delta-v in the normal direction, in meters per second.")
    radial: float = Field(description="The magnitude of the maneuver nodes delta-v in the radial direction, in meters per second.")
    delta_v: float = Field(description="The delta-v of the maneuver node, in meters per second. Does not change when executing the maneuver node. See remaining_delta_v.")
    remaining_delta_v: float = Field(description="Gets the remaining delta-v of the maneuver node, in meters per second. Changes as the node is executed.")
    ut: float = Field(description="The universal time at which the maneuver will occur, in seconds.")
    time_to: float = Field(description="The time until the maneuver node will be encountered, in seconds.")
    new_orbit: Orbit

@with_default_category("AutopilotService")
class AutopilotService(CommandSet):
    def __init__(self, krpc_connection):
        """Autopilot class."""
        super().__init__()

        self.connection = krpc_connection
        self.pilot = self.connection.mech_jeb

    plan_apoapsis_maneuver_parser = Cmd2ArgumentParser()
    plan_apoapsis_maneuver_parser.add_argument(
        "--new_apoapsis",
        type=float,
        required=True,
        help="The new apoapsis altitude [km]",
    )

    @with_argparser(plan_apoapsis_maneuver_parser)
    def do_plan_apoapsis_maneuver(self, args):
        """Plan an apoapsis change."""
        plan_apoapsis_parser = Cmd2ArgumentParser()
        plan_apoapsis_parser.add_argument(
            "new_apoapsis", type=float, help="The new apoapsis altitude"
        )
        output = self.plan_apoapsis_maneuver(args.new_apoapsis)

        self._cmd.poutput(output)

    def plan_apoapsis_maneuver(self, new_apoapsis: float):
        """Create a maneuver to set a new apoapsis

        new_apoapsis [km]
        """
        print("creating new nodes")
        planner = self.pilot.maneuver_planner.operation_apoapsis

        planner.new_apoapsis = new_apoapsis * 1000
        # planner.time_selector.time_reference.computed
        nodes = planner.make_nodes()

        warning = planner.error_message
        if warning:
            print(warning)

    def do_execute_nodes(self):
        output = self.execute_nodes()

        self._cmd.poutput(output)

    def execute_nodes(self):
        print("Executing maneuver nodes")
        executor = self.pilot.node_executor
        executor.execute_all_nodes()

        with self.connection.stream(getattr, executor, "enabled") as enabled:
            enabled.rate = (
                1  # we don't need a high throughput rate, 1 second is more than enough
            )
            with enabled.condition:
                while enabled():
                    enabled.wait()
