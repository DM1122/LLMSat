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
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PayloadManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, vessel=None):
        if PayloadManager._initialized:
            return
        self.vessel = vessel
        PayloadManager._initialized = True

    @staticmethod
    def _get_instance():
        return PayloadManager()

    def _get_experiment_obj(self, name):
        experiment_objs = self.vessel.parts.experiments

        for experiment in experiment_objs:
            if experiment.title == name:
                return experiment


    @staticmethod
    @tool
    def get_experiments() -> str:
        """Get information about all available experiments"""
        experiment_objs = PayloadManager._get_instance().vessel.parts.experiments

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
    
    @staticmethod
    @tool
    def run_experiment(name) -> str:
        """Run a given experiment"""
        exp_obj = PayloadManager._get_instance()._get_experiment_obj(name=name)
        result = exp_obj.run()
        return result

    @staticmethod
    @tool
    def transmit_experiment(name) -> str:
        """Transmit data produced by a given experiment"""
        exp_obj = PayloadManager._get_instance()._get_experiment_obj(name=name)
        result = exp_obj.transmit()
        return result

    @staticmethod
    @tool
    def dump_experiment(name) -> str:
        """Delete data produced by a given experiment"""
        exp_obj = PayloadManager._get_instance()._get_experiment_obj(name=name)
        result = exp_obj.dump()
        return result

    @staticmethod
    @tool
    def reset_experiment(name) -> str:
        """Reset a given experiment"""
        exp_obj = PayloadManager._get_instance()._get_experiment_obj(name=name)
        result = exp_obj.reset()
        return result