"""OrbitPropagator class."""

from datetime import datetime, timedelta

from cmd2 import CommandSet, with_argparser, with_default_category
from sqlalchemy import DateTime

from llmsat.libs import utils
from llmsat.libs.krpc_types import Orbit
import pandas as pd
from beartype import beartype


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
        epilog=utils.format_return_obj_str(Orbit),
    )

    @with_argparser(get_orbit_parser)
    def do_get_orbit(self, _=None):
        """The current orbit of the vessel."""
        orbit = self.get_orbit()

        self._cmd.poutput(orbit.model_dump_json(indent=4), timestamp=True)

    def get_orbit(self) -> Orbit:
        """The current orbit of the vessel."""

        orbit = Orbit(self.vessel.orbit)

        return orbit

    def do_radius_at(ut_start, ut_end):
        pass

    @beartype
    def radius_at(self, date: datetime, date_end: datetime = None) -> pd.DataFrame:
        """The orbital radius at the given time or over time range, in meters."""

        if date_end is None:
            # Single time point
            ut = utils.datetime_to_ksp_ut(date)
            radius = self.vessel.orbit.radius_at(ut)
            return pd.DataFrame({"radius": [radius]}, index=[date])
        else:
            if date_end < date:
                raise ValueError("ut_end must be after ut")

            # Time range
            time_range = pd.date_range(start=date, end=date_end, periods=100)
            radii = [
                self.vessel.orbit.radius_at(utils.datetime_to_ksp_ut(t))
                for t in time_range
            ]
            return pd.DataFrame({"radius": radii}, index=time_range)

    def validate_orbit(self):
        """Check orbit altitude from orbiting body does not drop below safety threshold"""

        orbit = self.get_orbit()

        date: datetime = utils.ksp_ut_to_datetime(self.connection.space_center.ut)

        date_end = date + timedelta(seconds=orbit.period)

        radii = self.radius_at(date, date_end)

        safe_altitude_threshold = 50000  # 50km above Enceladus
        enceladus_radius = 252100  # m

        # Check if any radius is below the safety threshold
        unsafe_radii = radii[
            radii["radius"] < safe_altitude_threshold + enceladus_radius
        ]

        if not unsafe_radii.empty:
            unsafe_period = (unsafe_radii.index.min(), unsafe_radii.index.max())
            altitude_range = (
                unsafe_radii["radius"].min() - enceladus_radius,
                unsafe_radii["radius"].max() - enceladus_radius,
            )
            raise ValueError(
                f"Orbit falls below safe altitude threshold of {safe_altitude_threshold} around {orbit.body} during {unsafe_period}. "
                f"Altitude range: {altitude_range} meters."
            )
        else:
            return True
