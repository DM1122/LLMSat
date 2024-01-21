"""OrbitPropagator class."""

from datetime import datetime, timedelta
from enum import Enum
from typing import List

import pandas as pd
from cmd2 import CommandSet, with_default_category
from pydantic import BaseModel

from llmsat.libs import utils


@with_default_category("OrbitPropagator")
class OrbitPropagator(CommandSet):
    """Functions for orbit determination."""

    def __init__(self, krpc_connection):
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

    def do_get_orbit(self, _):
        """Get the spacecraft's current orbit properties"""
        orbit = self.get_orbit()
        time = utils.get_ut(self.connection)

        self._cmd.poutput(
            f"Orbit properties at {time.isoformat()}:\n{orbit.model_dump_json(indent=4)}"
        )

    def get_orbit(self) -> utils.Orbit:
        """Get the spacecraft's current orbit properties"""

        orbit = utils.Orbit(self.vessel.orbit)

        return orbit

    def get_radius_at_time(time: datetime) -> float:
        pass

    def get_position_at_time(time: datetime):
        pass
