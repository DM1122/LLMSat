import json
import time
from pathlib import Path

import krpc
import numpy as np
from langchain.tools import tool
from langchain.tools.base import ToolException
from pydantic import BaseModel


class ExperimentProperties(BaseModel):
    """Basic properties of the spacecraft"""

    part: str
    name: str
    deployed: bool
    rerunnable: bool
    inoperable: bool
    has_data: bool
    available: bool


class DataProperties(BaseModel):
    description: str
    data_amount: float


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
        instance = PayloadManager()
        if instance.vessel is None:
            raise ValueError(
                "PayloadManager must be initialized with a vessel before calling its methods."
            )
        return PayloadManager()

    def _get_experiment_obj(self, name):
        experiment_objs = self.vessel.parts.experiments

        for experiment in experiment_objs:
            if experiment.title == name:
                return experiment

    @staticmethod
    @tool(handle_tool_error=True)
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
    @tool(handle_tool_error=True)
    def run_experiment(name) -> str:
        """Run a given experiment"""
        exp_obj = PayloadManager._get_instance()._get_experiment_obj(name=name)
        if exp_obj is None:
            raise ToolException(f"No experiment found with the name '{name}'.")
        exp_obj.run()

        time.sleep(1)
        data = exp_obj.data[0]
        subject = exp_obj.science_subject

        result = DataProperties(description=subject.title, data_amount=data.data_amount)

        return json.dumps(result, indent=4, default=lambda o: o.dict())

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
