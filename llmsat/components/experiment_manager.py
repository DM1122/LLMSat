"""Payload manager class."""
import argparse
import json
import time

from cmd2 import CommandSet, with_argparser, with_default_category
from pydantic import BaseModel

from llmsat.libs import utils




@with_default_category("ExperimentManager")
class ExperimentManager(CommandSet):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ExperimentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        """Experiment manager class."""
        if ExperimentManager._initialized:
            return
        super().__init__()

        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

        ExperimentManager._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return ExperimentManager()._cmd

    run_experiment_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        epilog=f"Returns:\nList[{DataProperties.model_json_schema()['title']}]: {json.dumps(DataProperties.model_json_schema()['properties'], indent=4)}",
    )
    run_experiment_parser.add_argument(
        "-name",
        type=str,
        required=True,
        help="name of experiment to run",
    )

    @with_argparser(run_experiment_parser)
    def do_run_experiment(self, args: argparse.Namespace):
        """Run a given experiment to acquire data."""
        try:
            data = self.run_experiment(args.name)
        except ValueError as e:
            self._cmd.poutput(e)
            return

        self._cmd.poutput(data.model_dump_json(indent=4))

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
