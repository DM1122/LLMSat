import krpc
from pydantic import BaseModel, validator
import astropy.units as unit

# class SpatialState(BaseModel):
#     """Simulated state properties"""

#     velocity_fixed: unit.Quantity
#     velocity_inertial: unit.Quantity
#     central_body: str
#     current_time: str
#     fixed_orientation: unit.Quantity
#     fixed_position: float
#     intertial_orientation: unit.Quantity
#     inertial_position: float

#     class Config:
#         arbitrary_types_allowed = True

#     @validator("velocity_fixed", "velocity_inertial", pre=True)
#     def validate_velocity(cls, value: unit.Quantity):
#         units = unit.meter / unit.second
#         shape = (3,)
#         if not value.unit.is_equivalent(units) or value.shape != shape:
#             raise ValueError("Quantity must be of units {units} and shape {shape}")
#         return value
    
#     @validator("fixed_orientation", "intertial_orientation", pre=True)
#     def validate_orientation(cls, value: unit.Quantity): 
#         units = unit.degree
#         shape = (3,)
#         if not value.unit.is_equivalent(units) or value.shape != shape:
#             raise ValueError("Quantity must be of units {units} and shape {shape}")
#         return value


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

