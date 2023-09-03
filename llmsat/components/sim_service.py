"""Simulator service"""

import json
from dataclasses import dataclass
from typing import TypeVar, Generic

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

T = TypeVar("T")

SPACECRAFT_PROPERTIES = Path("./spacecraft_properties.json")


@dataclass
class SpacecraftProperties:
    """Basic properties of the spacecraft"""

    name: str
    mass: int
    intertia_matrix: dict
    description: str


@dataclass
class ScenarioConfig:
    """Scenario configuration"""

    name: str
    period_start: str
    period_end: str


class SimService:
    """Service to interface with the environment simulator"""

    def __init__(
        self, scenario_config_file_path: Path, spacecraft_config_file_path: Path
    ):
        scenario_config = load_scenario_config(file_path=scenario_config_file_path)
        spacecraft_config = load_spacecraft_properties(
            file_path=spacecraft_config_file_path
        )

        print("Launching STK...")
        stk = STKDesktop.StartApplication(visible=True, userControl=True)

        stk_root = stk.Root

        print("Creating scenario...")
        stk_root.NewScenario(scenario_config.name)
        scenario_obj: IAgStkObject = stk_root.CurrentScenario
        scenario: IAgScenario = scenario_obj  # type: ignore

        scenario.SetTimePeriod(scenario_config.period_start, scenario_config.period_end)
        stk_root.Rewind()

        # configure satellite
        satellite: IAgSatellite = scenario_obj.Children.New(eClassType=AgESTKObjectType.eSatellite, instName=spacecraft_config.name)  # type: ignore
        satellite.MassProperties.Mass = spacecraft_config.mass
        satellite.MassProperties.Inertia.Ixx = spacecraft_config.intertia_matrix.


        propagator = satellite.Propagator
        orbitState = propagator.InitialState.Representation
        orbitStateClassical = orbitState.ConvertTo(
            AgEOrbitStateType.eOrbitStateClassical
        )

        input("Press any key to quit...")
        stk.ShutDown()

        print("Closed STK successfully.")


def load_scenario_config(file_path: Path) -> ScenarioConfig:  # todo: leverage generics
    """Loads the config"""
    with open(file_path, "r") as f:
        config_dict = json.load(f)

    # validate that the JSON contains all needed keys
    for field in ScenarioConfig.__annotations__:
        if field not in config_dict:
            raise ValueError(f"Missing field '{field}' in config file")

    return ScenarioConfig(**config_dict)


def load_spacecraft_properties(file_path: Path) -> SpacecraftProperties:
    """Loads the properties from disk"""
    with open(file_path, "r") as f:
        config_dict = json.load(f)

    # validate that the JSON contains all needed keys
    for field in SpacecraftProperties.__annotations__:
        if field not in config_dict:
            raise ValueError(f"Missing field '{field}' in config file")

    return SpacecraftProperties(**config_dict)


if __name__ == "__main__":
    x = SimService(
        scenario_config_file_path=Path("./llmsat/config/scenario.json"),
        spacecraft_config_file_path=Path("./llmsat/config/spacecraft.json"),
    )
