import krpc
from pydantic import BaseModel
from pathlib import Path
import numpy as np
from langchain.tools import tool
import json


class ExperimentProperties(BaseModel):
    """Basic properties of the spacecraft"""

    part: str
    name: str
    deployed: bool
    rerunnable: bool
    inoperable: bool
    has_data: bool
    available: bool


class PayloadManager:
    def __init__(self, vessel):
        self.vessel = vessel

    @tool
    def get_experiments(self) -> str:
        """Get information about all available experiments"""
        experiment_objs = self.vessel.parts.experiments

        experiments: dict[str, ExperimentProperties] = {}
        for obj in experiment_objs:
            props = ExperimentProperties(
                name=obj.title,
                part=obj.part.title,
                deployed=obj.deployed,
                rerunnable=obj.rerunnable,
                inoperable=obj.inoperable,
                has_data=obj.has_data,
                available=obj.available,
            )

            experiments[obj.title] = props

        return json.dumps(experiments, indent=4, default=lambda o: o.dict())

    @tool
    def run_experiment(self, name) -> str:
        """Run a given experiment"""
        exp_obj = self._get_experiment_obj(name=name)
        result = exp_obj.run()
        return result

    @tool
    def transmit_experiment(self, name) -> str:
        """Transmit data produced by a given experiment"""
        exp_obj = self._get_experiment_obj(name=name)
        result = exp_obj.transmit()
        return result

    @tool
    def dump_experiment(self, name) -> str:
        """Delete data produced by a given experiment"""
        exp_obj = self._get_experiment_obj(name=name)
        result = exp_obj.dump()
        return result

    @tool
    def reset_experiment(self, name) -> str:
        """Reset a given experiment"""
        exp_obj = self._get_experiment_obj(name=name)
        result = exp_obj.reset()
        return result

    def _get_experiment_obj(self, name):
        experiment_objs = self.vessel.parts.experiments

        for experiment in experiment_objs:
            if experiment.title == name:
                return experiment
