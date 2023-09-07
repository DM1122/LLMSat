"""Simulator service"""

import json
from pydantic import BaseModel, validator

from pathlib import Path
from agi.stk12.stkdesktop import STKDesktop
from pathlib import Path
import numpy as np
from agi.stk12.stkobjects import (
    AgESTKObjectType,
    AgEVePropagatorType,
    IAgVeInitialState,
    IAgScenario,
    IAgStkObject,
    IAgSatellite,
    AgEClassicalSizeShape,
    IAgProvideSpatialInfo,
    IAgSpatialState,
    AgEOrientationAscNode,
    AgEClassicalLocation,
)
import astropy.units as unit
from agi.stk12.stkutil import AgEOrbitStateType, IAgOrbitState, AgEEulerOrientationSequence


SPACECRAFT_PROPERTIES = Path("./spacecraft_properties.json")


class OrbitConfig(BaseModel):
    """Orbit config"""

    a: float
    e: float
    i: float
    w: float
    omega: float
    v: float


class ScenarioConfig(BaseModel):
    """Scenario configuration"""

    name: str
    period_start: str
    period_end: str
    timestep: float
    orbit: OrbitConfig


class IntertiaMatrixConfig(BaseModel):
    """Inertia matrix"""

    I_xx: float
    I_xy: float
    I_xz: float
    I_yy: float
    I_yz: float
    I_zz: float


class SpacecraftConfig(BaseModel):
    """Basic properties of the spacecraft"""

    name: str
    description: str
    mass: int
    inertia: IntertiaMatrixConfig


class SpatialState(BaseModel):
    """Simulated state properties"""

    velocity_fixed: unit.Quantity
    velocity_inertial: unit.Quantity
    central_body: str
    current_time: str
    fixed_orientation: unit.Quantity
    fixed_position: float
    intertial_orientation: unit.Quantity
    inertial_position: float

    class Config:
        arbitrary_types_allowed = True

    @validator("velocity_fixed", "velocity_inertial", pre=True)
    def validate_velocity(cls, value: unit.Quantity):
        units = unit.meter / unit.second
        shape = (3,)
        if not value.unit.is_equivalent(units) or value.shape != shape:
            raise ValueError("Quantity must be of units {units} and shape {shape}")
        return value
    
    @validator("fixed_orientation", "intertial_orientation", pre=True)
    def validate_orientation(cls, value: unit.Quantity): 
        units = unit.degree
        shape = (3,)
        if not value.unit.is_equivalent(units) or value.shape != shape:
            raise ValueError("Quantity must be of units {units} and shape {shape}")
        return value


class SimService:
    """Service to interface with the environment simulator"""

    def __init__(
        self, scenario_config_file_path: Path, spacecraft_config_file_path: Path
    ):
        # load config
        with open(scenario_config_file_path, "r") as f:
            config = json.load(f)
        self.scenario_config = ScenarioConfig(**config)

        with open(spacecraft_config_file_path, "r") as f:
            config = json.load(f)
        self.spacecraft_config = SpacecraftConfig(**config)

        # create stk scenario
        print("Launching STK...")
        self.stk = STKDesktop.StartApplication(visible=True, userControl=True)

        print("Creating scenario...")
        self.stk.Root.NewScenario(self.scenario_config.name)
        scenario_obj: IAgStkObject = self.stk.Root.CurrentScenario
        scenario: IAgScenario = scenario_obj  # type: ignore

        scenario.SetTimePeriod(
            self.scenario_config.period_start, self.scenario_config.period_end
        )
        self.stk.Root.Rewind()
        self.epoch = self.scenario_config.period_start

        self.satellite: IAgSatellite = scenario_obj.Children.New(eClassType=AgESTKObjectType.eSatellite, instName=self.spacecraft_config.name)  # type: ignore
        self.satellite.MassProperties.Mass = self.spacecraft_config.mass
        self.satellite.MassProperties.Inertia.Ixx = self.spacecraft_config.inertia.I_xx
        self.satellite.MassProperties.Inertia.Ixy = self.spacecraft_config.inertia.I_xy
        self.satellite.MassProperties.Inertia.Ixz = self.spacecraft_config.inertia.I_xz
        self.satellite.MassProperties.Inertia.Iyy = self.spacecraft_config.inertia.I_yy
        self.satellite.MassProperties.Inertia.Iyz = self.spacecraft_config.inertia.I_yz
        self.satellite.MassProperties.Inertia.Izz = self.spacecraft_config.inertia.I_zz

        # configure init orbit
        self.satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
        propagator = self.satellite.Propagator
        orbitState: IAgOrbitState = propagator.InitialState.Representation  # type: ignore
        orbitStateClassical: IAgOrbitState = orbitState.ConvertTo(
            AgEOrbitStateType.eOrbitStateClassical
        )
        orbitStateClassical.SizeShapeType = (
            AgEClassicalSizeShape.eSizeShapeSemimajorAxis
        )
        sizeShape = orbitStateClassical.SizeShape
        sizeShape.Eccentricity = self.scenario_config.orbit.e
        sizeShape.SemiMajorAxis = self.scenario_config.orbit.a
        orientation = orbitStateClassical.Orientation
        orientation.Inclination = self.scenario_config.orbit.i
        orientation.ArgOfPerigee = self.scenario_config.orbit.w
        orientation.AscNodeType = AgEOrientationAscNode.eAscNodeRAAN
        raan = orientation.AscNode
        raan.Value = self.scenario_config.orbit.omega
        orbitStateClassical.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
        trueAnomaly = orbitStateClassical.Location
        trueAnomaly.Value = self.scenario_config.orbit.v

        orbitState.Assign(orbitStateClassical)

    def shutdown(self):
        """Terminate the simulation"""
        self.stk.ShutDown()

    def step_forward(self):
        """Step the simulation forward"""
        self.stk.Root.CurrentTime += self.scenario_config.timestep

    def get_spatial_state(self) -> SpatialState:
        spatial_info_obj: IAgProvideSpatialInfo = self.satellite  # type: ignore
        spatial_info = spatial_info_obj.GetSpatialInfo(recycle=False)
        state_obj: IAgSpatialState = spatial_info.GetState(time=self.epoch)

        velocity_fixed: unit.Quantity = (
            np.array(state_obj.QueryVelocityFixed()) * unit.meter / unit.second
        )

        velocity_inertial: unit.Quantity = (
            np.array(state_obj.QueryVelocityInertial()) * unit.meter / unit.second
        )

        fixed_orientation: unit.Quantity = (
            np.array(state_obj.FixedOrientation.QueryEulerAngles(sequence=AgEEulerOrientationSequence.e123)) * unit.degree
        )

        inertial_orientation: unit.Quantity = (
            np.array(state_obj.InertialOrientation.QueryEulerAngles(sequence=AgEEulerOrientationSequence.e123)) * unit.degree
        )

        state = SpatialState(
            velocity_fixed=velocity_fixed,
            velocity_inertial=velocity_inertial,
            central_body=state_obj.CentralBody,
            current_time=state_obj.CurrentTime,
            fixed_orientation=fixed_orientation,
            fixed_position=state_obj.FixedPosition,
            intertial_orientation=inertial_orientation,
            inertial_position=state_obj.InertialPosition,
        )

        

        return state
