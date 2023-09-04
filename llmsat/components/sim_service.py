"""Simulator service"""

import json
from pydantic import BaseModel

from pathlib import Path
from agi.stk12.stkdesktop import STKDesktop
from pathlib import Path
from agi.stk12.stkobjects import (
    AgESTKObjectType,
    AgEVePropagatorType,
    IAgScenario,
    IAgStkObject,
    IAgSatellite,
)
from agi.stk12.stkutil import AgEOrbitStateType


SPACECRAFT_PROPERTIES = Path("./spacecraft_properties.json")

class ScenarioConfig(BaseModel):
    """Scenario configuration"""

    name: str
    period_start: str
    period_end: str


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
        
        with open(scenario_config_file_path, "r") as f:
            config = json.load(f)
            print(config)
        self.scenario_config = ScenarioConfig(**config)

        with open(spacecraft_config_file_path, "r") as f:
            config = json.load(f)
        self.spacecraft_config = SpacecraftConfig(**config)

        # print("Launching STK...")
        # stk = STKDesktop.StartApplication(visible=True, userControl=True)

        # stk_root = stk.Root

        # print("Creating scenario...")
        # stk_root.NewScenario(self.scenario_config.name)
        # scenario_obj: IAgStkObject = stk_root.CurrentScenario
        # scenario: IAgScenario = scenario_obj  # type: ignore

        # scenario.SetTimePeriod(self.scenario_config.period_start, self.scenario_config.period_end)
        # stk_root.Rewind()

        # # configure satellite
        # satellite: IAgSatellite = scenario_obj.Children.New(eClassType=AgESTKObjectType.eSatellite, instName=self.spacecraft_config.name)  # type: ignore
        # satellite.MassProperties.Mass = self.spacecraft_config.mass
        # satellite.MassProperties.Inertia.Ixx = self.spacecraft_config.inertia


        # propagator = satellite.Propagator
        # orbitState = propagator.InitialState.Representation
        # orbitStateClassical = orbitState.ConvertTo(
        #     AgEOrbitStateType.eOrbitStateClassical
        # )

        # input("Press any key to quit...")
        # stk.ShutDown()

        # print("Closed STK successfully.")
    
