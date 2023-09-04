from enum import Enum, auto
import astropy.units as unit
from astropy.units import Quantity
from pydantic import BaseModel

class ADCSState(Enum):
    SAFE = auto()
    DETUMBLING = auto()
    SUN_POINTING = auto()
    FINE_POINTING = auto()
    TRACKING = auto()

class SensorData(BaseModel):

    rotation_rate: unit.deg / unit.s



class ADCS:
    def __init__(self):
        self.current_state = ADCSState.DETUMBLING

        pass


    def update(self):
        self.sensor_data = self._read_sensors()

        max_rot = 1f * unit.deg
        if self.sensor_data.rotation_rate > 1:
            pass


        

    def set_mode(self, mode: ADCSState):
        self.current_state = mode


    def _read_sensors(self) -> SensorData:
        data = SensorData(rotation_rate=5)

        return data



    