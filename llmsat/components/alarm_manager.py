from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime


class Alarm(BaseModel):
    """Alarm object"""

    name: str
    description: str
    epoch: datetime


class AlarmManager:
    """Alarm setting and storage"""

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

    def check_alarms(self, epoch: datetime) -> List[Alarm]:
        """Returns alarms that are older than the provided epoch and removes them"""
        expired_alarms: List[Alarm] = []

        # Create a list of keys to iterate over
        alarm_ids = list(self.alarms.keys())

        for id in alarm_ids:
            if epoch >= self.alarms[id].epoch:
                # alarm has expired
                expired_alarms.append(self.alarms.pop(id))

        return expired_alarms
