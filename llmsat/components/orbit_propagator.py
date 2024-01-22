"""OrbitPropagator class."""

from datetime import datetime, timedelta
from enum import Enum
from typing import List

import pandas as pd
from cmd2 import CommandSet, with_default_category
from pydantic import BaseModel
from cmd2 import CommandSet, with_argparser, with_default_category
from llmsat.libs.krpc_types import Orbit
from llmsat.libs import utils
import json


@with_default_category("OrbitPropagator")
class OrbitPropagator(CommandSet):
    """Functions for orbit determination."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OrbitPropagator, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        if OrbitPropagator._initialized:
            return
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

        OrbitPropagator._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return OrbitPropagator()._cmd

    get_orbit_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
        epilog=f"Returns:\n{json.dumps(Orbit.model_json_schema()['$defs']['Orbit'], indent=4)}",  # need to turn this into utility function
    )

    @with_argparser(get_orbit_parser)
    def do_get_orbit(self, _=None):
        """The current orbit of the vessel."""
        orbit = self.get_orbit()

        self._cmd.poutput(orbit.model_dump_json(indent=4))

    def get_orbit(self) -> Orbit:
        """The current orbit of the vessel."""

        orbit = Orbit(self.vessel.orbit)

        return orbit

    def get_radius_at_time(time: datetime) -> float:  # make this a range
        pass

    def get_position_at_time(time: datetime):
        pass
