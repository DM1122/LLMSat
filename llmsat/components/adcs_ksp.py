import astropy.units as unit
import krpc
from pydantic import BaseModel, validator


class OrbitProperties(BaseModel):
    """Prbit Properties"""

    body: str
    apoapsis_altitude: unit.Quantity
    periapsis_altitude: unit.Quantity
    semi_major_axis: unit.Quantity
    semi_major_axis: unit.Quantity
    radius: unit.Quantity
    speed: unit.Quantity
    period: unit.Quantity
    time_to_apoapsis: unit.Quantity
    time_to_periapsis: unit.Quantity
    eccentricity: float
    inclination: unit.Quantity
    epoch: unit.Quantity


class ADCS:

    def __init__(self, vessel):

        self.vessel = vessel

    def get_orbit_properties(self):
        """The celestial body (e.g. planet or moon) around which the vessel is orbiting"""

        properties = OrbitProperties(
            body=self.vessel.orbit.body, 
            apoapsis_altitude=self.vessel.orbit.apoapsis_altitude)

        return properties
    

    def get_apoapsis_altitude(self):

