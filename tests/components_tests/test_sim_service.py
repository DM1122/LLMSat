"""Sim service tests"""
from llmsat.components.sim_service import SimService
from pathlib import Path

CONFIG_PATH = Path("./llmsat/config/")

def test_constructor():
    service = SimService(scenario_config_file_path=CONFIG_PATH / "scenario.json", spacecraft_config_file_path=CONFIG_PATH / "spacecraft.json")
    
    print(service.scenario_config)
    print(service.spacecraft_config)
