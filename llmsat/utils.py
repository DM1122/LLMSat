"""Game-related utilities"""

import functools
import inspect
import json
import os
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field


class Orbit(BaseModel):
    """Orbit parameters"""

    body: str = Field(
        description="The celestial body (e.g. planet or moon) around which the object is orbiting."
    )
    apoapsis: float = Field(
        description="[m] Gets the apoapsis of the orbit from the center of mass of the body being orbited."
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
    speed: float = Field(
        description="The orbital speed of the object in meters per second. This value will change over time if the orbit is elliptical."
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
    time_to_soi_change: float = Field(
        description="The time until the object changes sphere of influence, in seconds. Returns NaN if the object is not going to change sphere of influence."
    )


def is_ksp_running():
    """Determine whether Kerbal Space Program is currently running on the system."""
    try:
        # List processes and grep for KSP
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8")
        return "KSP" in output
    except:
        return False


def launch_ksp(path: Path):
    subprocess.Popen([path], cwd=os.path.dirname(path))


def load_checkpoint(name: str, space_center):
    """Load the given game save state"""
    try:
        space_center.load(name)
    except ValueError as e:
        raise ValueError(
            f"No checkpoint named '{name}.sfs' was found. Please create one"
        )


def load_json(filename):
    """Load a given JSON file"""

    with open(filename, "r") as file:
        data = json.load(file)
    return data


def cast_krpc_orbit(obj) -> Orbit:
    """Casts a KRPC orbit object to an Orbit model"""
    orbit = Orbit(
        body=obj.body.name,
        apoapsis=obj.apoapsis,
        periapsis=obj.periapsis,
        apoapsis_altitude=obj.apoapsis_altitude,
        periapsis_altitude=obj.periapsis_altitude,
        semi_major_axis=obj.semi_major_axis,
        semi_minor_axis=obj.semi_minor_axis,
        radius=obj.radius,
        speed=obj.speed,
        period=obj.period,
        time_to_apoapsis=obj.time_to_apoapsis,
        time_to_periapsis=obj.time_to_periapsis,
        time_to_soi_change=obj.time_to_soi_change,
        eccentricity=obj.eccentricity,
        inclination=obj.inclination,
        longitude_of_ascending_node=obj.longitude_of_ascending_node,
        argument_of_periapsis=obj.argument_of_periapsis,
        mean_anomaly_at_epoch=obj.mean_anomaly_at_epoch,
        epoch=obj.epoch,
    )

    return orbit


class MET:
    """Mission elapsed time object."""

    def __init__(self, seconds):
        self.seconds = int(seconds)

    def __str__(self):
        # Constants for time calculations
        seconds_in_minute = 60
        seconds_in_hour = 3600
        seconds_in_day = 86400
        seconds_in_year = 31536000  # Approximation, not accounting for leap years

        # Calculate years, days, hours, minutes, and seconds
        years, remaining_seconds = divmod(self.seconds, seconds_in_year)
        days, remaining_seconds = divmod(remaining_seconds, seconds_in_day)
        hours, remaining_seconds = divmod(remaining_seconds, seconds_in_hour)
        minutes, seconds = divmod(remaining_seconds, seconds_in_minute)

        return f"T+ {years:01}Y, {days:03}D, {hours:02}:{minutes:02}:{seconds:02}"
