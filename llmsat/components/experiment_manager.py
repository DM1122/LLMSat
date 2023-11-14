"""Payload manager class."""
import json
import time
from typing import List

from llmsat import utils
from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field


class Experiment(BaseModel):
    """Experiment properties"""

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


@with_default_category("ExperimentManager")
class ExperimentManager(CommandSet):
    def __init__(self, krpc_connection):
        """Experiment manager class."""
        super().__init__()

        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

    def _get_experiment_obj(self, name):
        """Retrieves the KRPC experiment object by name"""
        experiment_objs = self.vessel.parts.experiments

        for experiment in experiment_objs:
            if experiment.title == name:
                return experiment

    def do_get_experiments(self, statement):
        """Get a dictionary of all onboard scientific experiments"""
        experiments = self.get_experiments()
        self._cmd.poutput(json.dumps(experiments, indent=4, default=lambda o: o.dict()))

    def get_experiments(self) -> dict[str, Experiment]:
        """Get information about all available experiments"""
        experiment_objs = self.vessel.parts.experiments

        experiments: dict[str, Experiment] = {}
        for obj in experiment_objs:
            experiment = Experiment(
                name=obj.title,
                part=obj.part.title,
                deployed=obj.deployed,
                rerunnable=obj.rerunnable,
                inoperable=obj.inoperable,
                has_data=obj.has_data,
                available=obj.available,
            )

            experiments[obj.title] = experiment

        return experiments

    run_experiment_parser = Cmd2ArgumentParser(
        epilog=f"Returns:\nList[{DataProperties.model_json_schema()['title']}]: {json.dumps(DataProperties.model_json_schema()['properties'], indent=4)}"
    )
    run_experiment_parser.add_argument(
        "-name",
        type=str,
        required=True,
        help="name of experiment to run",
    )

    @with_argparser(run_experiment_parser)
    def do_run_experiment(self, args):
        """Run a given experiment to acquire data"""
        data = self.run_experiment(args.name)
        self._cmd.poutput(data.model_dump_json(indent=4))

    def run_experiment(self, name: str) -> DataProperties:
        """Run a given experiment"""
        exp_obj = self._get_experiment_obj(name=name)
        if exp_obj is None:
            raise ValueError(f"No experiment found with the name '{name}'.")

        self._cmd.poutput(f"Running experiment {name}...")
        exp_obj.run()

        time.sleep(1)  # give the simulator time to run experiment

        data = exp_obj.data[0]  # TODO: handle multiple data
        subject = exp_obj.science_subject

        result = DataProperties(description=subject.title, data_amount=data.data_amount)

        return result
