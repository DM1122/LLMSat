from enum import Enum, auto

import astropy.units as unit
from astropy.units import Quantity
from pydantic import BaseModel

from llmsat.components.sim_service import SimService


class ADCSState(Enum):
    """ADCS states"""

    SAFE = auto()
    DETUMBLING = auto()
    SUN_POINTING = auto()
    FINE_POINTING = auto()
    TRACKING = auto()


class SensorData(BaseModel):
    """ADCS sensor data obtained through sim environment"""

    rotation_rate: unit.deg / unit.s


class ADCS:
    def __init__(self, env: SimService):
        self.env = env
        self.current_state = ADCSState.DETUMBLING

        pass

    def update(self):
        self.sensor_data = self._read_sensors()

        max_rot = 1 * unit.deg
        if self.sensor_data.rotation_rate > 1:
            pass

    def set_mode(self, mode: ADCSState):
        self.current_state = mode

    def _read_sensors(self) -> SensorData:
        data = SensorData(rotation_rate=self.env.get_rotation_rate())

        return data
