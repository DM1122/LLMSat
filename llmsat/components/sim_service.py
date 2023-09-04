"""Simulator service"""

import json
from pydantic import BaseModel

from pathlib import Path
from agi.stk12.stkdesktop import STKDesktop
from pathlib import Path
from agi.stk12.stkobjects import (
    AgESTKObjectType,
    AgEVePropagatorType,
    IAgVeInitialState,
    IAgScenario,
    IAgStkObject,
    IAgSatellite,
    AgEClassicalSizeShape
)
from agi.stk12.stkutil import AgEOrbitStateType, IAgOrbitState


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


class SimService:
    """Service to interface with the environment simulator"""

    def __init__(
        self, scenario_config_file_path: Path, spacecraft_config_file_path: Path
    ):
        # load config
        with open(scenario_config_file_path, "r") as f:
            config = json.load(f)
            print(config)
        self.scenario_config = ScenarioConfig(**config)

        with open(spacecraft_config_file_path, "r") as f:
            config = json.load(f)
        self.spacecraft_config = SpacecraftConfig(**config)

        # create stk scenario
        print("Launching STK...")
        stk = STKDesktop.StartApplication(visible=True, userControl=True)
        stk_root = stk.Root

        print("Creating scenario...")
        stk_root.NewScenario(self.scenario_config.name)
        scenario_obj: IAgStkObject = stk_root.CurrentScenario
        scenario: IAgScenario = scenario_obj  # type: ignore

        scenario.SetTimePeriod(self.scenario_config.period_start, self.scenario_config.period_end)
        stk_root.Rewind()

        satellite: IAgSatellite = scenario_obj.Children.New(eClassType=AgESTKObjectType.eSatellite, instName=self.spacecraft_config.name)  # type: ignore
        satellite.MassProperties.Mass = self.spacecraft_config.mass
        satellite.MassProperties.Inertia.Ixx = self.spacecraft_config.inertia.I_xx
        satellite.MassProperties.Inertia.Ixy = self.spacecraft_config.inertia.I_xy
        satellite.MassProperties.Inertia.Ixz = self.spacecraft_config.inertia.I_xz
        satellite.MassProperties.Inertia.Iyy = self.spacecraft_config.inertia.I_yy
        satellite.MassProperties.Inertia.Iyz = self.spacecraft_config.inertia.I_yz
        satellite.MassProperties.Inertia.Izz = self.spacecraft_config.inertia.I_zz

        # configure init orbit
        satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
        propagator = satellite.Propagator
        orbitState: IAgOrbitState = propagator.InitialState.Representation # type: ignore
        orbitStateClassical: IAgOrbitState = orbitState.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)
        orbitStateClassical.SizeShapeType = AgEClassicalSizeShape.eSizeShapeSemimajorAxis
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

        input("Press any key to quit...")
        stk.ShutDown()

        print("Closed STK successfully.")
    
