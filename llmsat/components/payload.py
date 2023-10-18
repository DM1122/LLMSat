import krpc
from pydantic import BaseModel, validator
from pathlib import Path
import numpy as np


class ExperimentProps(BaseModel):
    """Basic properties of the spacecraft"""

    name: str
    deployed: bool
    rerunnable: bool
    inoperable: bool
    has_data: bool
    available: bool


class PayloadManager:
    def __init__(self, vessel):
        self.vessel = vessel

    def get_experiments(self):
        experiment_objs = self.vessel.parts.experiments

        experiments = []

        for obj in experiment_objs:
            props = ExperimentProps(
                name=obj.title,
                deployed=obj.deployed,
                rerunnable=obj.rerunnable,
                inoperable=obj.inoperable,
                has_data=obj.has_data,
                available=obj.available,
            )

            experiments.append(props)

        return experiments
