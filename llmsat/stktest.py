from agi.stk12.stkdesktop import STKDesktop
from pathlib import Path
from agi.stk12.stkobjects import (
    AgEClassicalLocation,
    AgEClassicalSizeShape,
    AgECvBounds,
    AgECvResolution,
    AgEFmCompute,
    AgEFmDefinitionType,
    AgEOrientationAscNode,
    AgESTKObjectType,
    AgEVePropagatorType,
    IAgScenario,
    IAgStkObject,
    IAgSatellite
)
from agi.stk12.stkutil import AgEOrbitStateType

SPACECRAFT_CONFIG = Path("./spacecraft_config.json")
SCENARIO = Path("./scenarios/mars/mars.sc")

if __name__ == "__main__":
    print("Launching STK...")
    stk = STKDesktop.StartApplication(visible=True, userControl=True)

    stk_root = stk.Root

    print("Creating scenario...")
    stk_root.NewScenario("LLMSatScenario")
    scenario_obj: IAgStkObject = stk_root.CurrentScenario
    scenario: IAgScenario = scenario_obj  # type: ignore
    scenario.SetTimePeriod("1 Jan 2030 00:00:00", "31 Dec 2031 00:00:00")
    stk_root.Rewind()

    satellite: IAgSatellite = scenario_obj.Children.New(AgESTKObjectType.eSatellite, "LLMSat-1") # type: ignore
    propagator = satellite.
    orbitState = propagator.InitialState.Representation
    orbitStateClassical = orbitState.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)

    input("Press any key to quit...")
    stk.ShutDown()

    print("Closed STK successfully.")
