from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class Alarm(BaseModel):
    """Alarm object"""

    name: str
    description: str
    epoch: datetime


class AlarmManager:

    def __init__(self):
        self.alarms: Dict[int, Alarm] = {}
        self.alarm_id_counter = 0

    def get_alarms(self) -> Dict[int, Alarm]:
        """Returns all alarms"""
        return self.alarms

    def set_alarm(self, name: str, description: str, epoch: datetime) -> None:
        """Adds a new alarm"""
        alarm = Alarm(name=name, description=description, epoch=epoch)
        self.alarms[self.alarm_id_counter] = alarm
        self.alarm_id_counter += 1

    def delete_alarm(self, id: int) -> None:
        """Deletes an alarm by its ID"""
        self.alarms.pop(id, None)

    def get_expired_alarms(self, epoch: datetime) -> Optional[Alarm]:
        """Returns alarms that are older than the provided epoch and removes them"""
        expired_alarms = [id for id, alarm in self.alarms.items() if epoch >= alarm.epoch]

        for id in expired_alarms:
            alarm = self.alarms.pop(id)
            return alarm



class OBC:
    """Onboard computer"""
    def __init__(self, alarm_manager: AlarmManager):
        self.alarm_manager = alarm_manager


    def get_spacecraft_properties(self) -> SpacecraftProperties:
        properties = {
            "mass [kg]": 4,
            "inertia_matrix [kg m^2]": {
                "XX": 1,
                "XY": 0,
                "XZ": 1,
                "YX": 0,
                "YY": 1,
                "YZ": 0,
                "ZX": 0,
                "ZY": 0,
                "ZZ": 1,
            },
        }

        return properties


    











if __name__ == "__main__":
    config = load_spacecraft_properties(SPACECRAFT_PROPERTIES)



