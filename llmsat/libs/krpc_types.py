"""kRPC Types"""

from datetime import datetime
from enum import Enum
from typing import List
from typing import Optional
from pydantic import BaseModel, Field

from llmsat.libs import utils


class Orbit(BaseModel):
    """Describes an orbit."""

    body: str = Field(
        description="The celestial body (e.g. planet or moon) around which the object is orbiting."
    )
    apoapsis: float = Field(
        description="Gets the apoapsis of the orbit, in meters, from the center of mass of the body being orbited."
    )
    periapsis: float = Field(
        description="The periapsis of the orbit, in meters, from the center of mass of the body being orbited."
    )
    apoapsis_altitude: float = Field(
        description="The apoapsis of the orbit, in meters, above the sea level of the body being orbited."
    )
    periapsis_altitude: float = Field(
        description="The periapsis of the orbit, in meters, above the sea level of the body being orbited."
    )
    semi_major_axis: float = Field(
        description="The semi-major axis of the orbit, in meters."
    )
    semi_minor_axis: float = Field(
        description="The semi-minor axis of the orbit, in meters."
    )
    radius: float = Field(
        description="The current radius of the orbit, in meters. This is the distance between the center of mass of the object in orbit, and the center of mass of the body around which it is orbiting."
    )
    period: float = Field(description="The orbital period, in seconds.")
    time_to_apoapsis: float = Field(
        description="The time until the object reaches apoapsis, in seconds."
    )
    time_to_periapsis: float = Field(
        description="The time until the object reaches periapsis, in seconds."
    )
    eccentricity: float = Field(description="The eccentricity of the orbit.")
    inclination: float = Field(description="The inclination of the orbit, in radians.")
    longitude_of_ascending_node: float = Field(
        description="The longitude of the ascending node, in radians."
    )
    argument_of_periapsis: float = Field(
        description="The argument of periapsis, in radians."
    )
    mean_anomaly_at_epoch: float = Field(description="The mean anomaly at epoch.")
    epoch: float = Field(
        description="The time since the epoch (the point at which the mean anomaly at epoch was measured, in seconds."
    )
    mean_anomaly: float = Field(description="The mean anomaly")
    eccentric_anomaly: float = Field(description="The eccentric anomaly")
    true_anomaly: float = Field(description="The true anomaly.")
    orbital_speed: float = Field(
        description="The current orbital speed in meters per second."
    )
    time_to_soi_change: float = Field(
        description="The time until the object changes sphere of influence, in seconds. Returns NaN if the object is not going to change sphere of influence."
    )
    next_orbit: Optional["Orbit"] = Field(
        description="If the object is going to change sphere of influence in the future, returns the new orbit after the change. Otherwise returns None."
    )

    def __init__(self, orbit_obj):
        super().__init__(
            body=orbit_obj.body.name,
            apoapsis=orbit_obj.apoapsis,
            periapsis=orbit_obj.periapsis,
            apoapsis_altitude=orbit_obj.apoapsis_altitude,
            periapsis_altitude=orbit_obj.periapsis_altitude,
            semi_major_axis=orbit_obj.semi_major_axis,
            semi_minor_axis=orbit_obj.semi_minor_axis,
            radius=orbit_obj.radius,
            period=orbit_obj.period,
            time_to_apoapsis=orbit_obj.time_to_apoapsis,
            time_to_periapsis=orbit_obj.time_to_periapsis,
            eccentricity=orbit_obj.eccentricity,
            inclination=orbit_obj.inclination,
            longitude_of_ascending_node=orbit_obj.longitude_of_ascending_node,
            argument_of_periapsis=orbit_obj.argument_of_periapsis,
            mean_anomaly_at_epoch=orbit_obj.mean_anomaly_at_epoch,
            epoch=orbit_obj.epoch,
            mean_anomaly=orbit_obj.mean_anomaly,
            eccentric_anomaly=orbit_obj.eccentric_anomaly,
            true_anomaly=orbit_obj.true_anomaly,
            orbital_speed=orbit_obj.orbital_speed,
            time_to_soi_change=orbit_obj.time_to_soi_change,
            next_orbit=orbit_obj.next_orbit,
        )


class Node(BaseModel):
    """A maneuver node"""

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
    ut: datetime = Field(
        description="The universal time at which the maneuver will occur, in seconds."
    )
    time_to: float = Field(
        description="The time until the maneuver node will be encountered, in seconds."
    )
    orbit: Orbit = Field(
        description="The orbit that results from executing the maneuver node."
    )

    def __init__(self, node_obj):
        super().__init__(
            prograde=node_obj.prograde,
            normal=node_obj.normal,
            radial=node_obj.radial,
            delta_v=node_obj.delta_v,
            remaining_delta_v=node_obj.remaining_delta_v,
            ut=utils.ksp_ut_to_datetime(node_obj.ut),
            time_to=node_obj.time_to,
            orbit=Orbit(node_obj.orbit),
        )


class Experiment(BaseModel):
    """Experiment properties"""

    part: str
    name: str
    deployed: bool
    rerunnable: bool
    inoperable: bool
    has_data: bool
    available: bool


class DataProperties(BaseModel):
    description: str
    data_amount: float


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
