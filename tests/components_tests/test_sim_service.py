"""Sim service tests"""
from llmsat.components.sim_service import SimService
from pathlib import Path
import pytest

CONFIG_PATH = Path("./llmsat/config/")


@pytest.fixture(scope="session")
def setup():
    service = SimService(
        scenario_config_file_path=CONFIG_PATH / "scenario.json",
        spacecraft_config_file_path=CONFIG_PATH / "spacecraft.json",
    )

    yield service

    service.shutdown()

def test_get_spatial_state(setup):
    service: SimService = setup
    state = service.get_spatial_state()
    
    print(state)
