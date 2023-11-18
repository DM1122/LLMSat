"""SpacecraftManager class."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat import utils


class Alarm(BaseModel):
    """An alarm"""

    id: int = Field(description="Unique identifier of the alarm")
    type: str = Field(description="Type of alarm")
    title: str = Field(description="Title of the alarm")
    description: str = Field(description="Description of the alarm")
    time: float = Field(description="Time the alarm will trigger")
    time_until: float = Field(description="Time until the alarm triggers")

    def __init__(self, alarm_obj, **data):
        super().__init__(
            id=alarm_obj.id,
            type=alarm_obj.type,
            title=alarm_obj.title,
            description=alarm_obj.description,
            time=alarm_obj.time,
            time_until=alarm_obj.time_until,
            **data,
        )


@with_default_category("AlarmManager")
class AlarmManager(CommandSet):
    """Functions for setting alarms."""

    def __init__(self, krpc_connection):
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel
        self.alarm_manager = self.connection.space_center.alarm_manager

    def do_get_alarms(self, _):
        """Get all alarms"""
        alarms = self.get_alarms()

        self._cmd.poutput(alarms)

    def get_alarms(self) -> List[Alarm]:
        """Get all alarms"""

        alarm_objs = self.alarm_manager.alarms
        alarms = []
        for alarm_obj in alarm_objs:
            alarm = Alarm(alarm_obj)
            alarms.append(alarm)

        return alarms

    add_alarm_parser = Cmd2ArgumentParser(
        epilog=f"Returns:\n{Alarm.model_json_schema()['title']}: {json.dumps(Alarm.model_json_schema()['properties'], indent=4)}"
    )
    add_alarm_parser.add_argument(
        "-title",
        type=str,
        required=True,
        help="Title for the alarm",
    )
    add_alarm_parser.add_argument(
        "-time",
        type=float,
        required=True,
        help="Number of seconds from now that the alarm should trigger",
    )
    add_alarm_parser.add_argument(
        "-description",
        type=str,
        required=False,
        help="Description for the alarm",
    )

    @with_argparser(add_alarm_parser)
    def do_add_alarm(self, args):
        """Create a new alarm"""
        new_alarm = self.add_alarm(
            title=args.title, time=args.time, description=args.description
        )

        self._cmd.poutput(f"New alarm created:\n{new_alarm}")

    def add_alarm(self, title, time, description) -> Alarm:
        """Create a new alarm"""

        alarm_obj = self.alarm_manager.add_vessel_alarm(
            time=time, vessel=self.vessel, title=title, description=description
        )

        alarm = Alarm(alarm_obj)

        return alarm
