"""SpacecraftManager class."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict

from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat import utils


class Alarm(BaseModel):
    """An alarm"""

    id: str = Field(description="Unique identifier of the alarm")
    name: str = Field(description="Name of the alarm")
    description: str = Field(description="Description of the alarm")
    time: datetime = Field(
        description="Universal time (in seconds) at which the alarm will trigger "
    )
    remaining: timedelta = Field(
        description="The number of seconds until the alarm will fire"
    )

    def __init__(self, alarm_obj, current_time: timedelta):
        super().__init__(
            id=alarm_obj.id,
            name=alarm_obj.name,
            description=alarm_obj.notes,
            time=utils.epoch + timedelta(seconds=alarm_obj.time),  # universal time
            remaining=timedelta(seconds=alarm_obj.time) - current_time,
        ),

    def formatted_time(self):
        return self.time.strftime("%d %b %Y, %H:%M:%S")

    def remaining_formatted(self):
        return utils.MET(self.remaining.seconds)

    # def get_remaining_time(self, alarm_obj) -> timedelta:
    #     """Built-in 'remaining' property does not work"""
    #     trigger_time_ut = utils.epoch + timedelta(seconds=alarm_obj.time)
    #     current_time_ut = utils.epoch + timedelta(
    #         seconds=self.connection.space_center.ut
    #     )

    #     time_remaining = trigger_time_ut - current_time_ut

    #     return time_remaining


@with_default_category("AlarmManager")
class AlarmManager(CommandSet):
    """Functions for setting alarms."""

    def __init__(self, krpc_connection, remove_alarms_on_init=True):
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel
        self.kac = self.connection.kerbal_alarm_clock

        if remove_alarms_on_init:
            self._remove_all_alarms()

    def do_get_alarms(self, statement):
        """Get all alarms"""
        alarms = self.get_alarms()

        if not alarms:
            self._cmd.poutput("No alarms have been set")
            return

        formatted_alarms = {}
        for alarm_id, alarm in alarms.items():
            alarm_dict = alarm.model_dump()
            alarm_dict["time"] = alarm.formatted_time()
            alarm_dict["remaining"] = str(
                alarm.remaining_formatted()
            )  # TODO: remove T+
            formatted_alarms[alarm_id] = alarm_dict

        self._cmd.poutput(json.dumps(formatted_alarms, indent=4))

    def get_alarms(self) -> Dict[int, Alarm]:
        """Get all alarms"""

        alarm_objs = self.kac.alarms
        alarms = {}
        for alarm_obj in alarm_objs:
            alarm = Alarm(
                alarm_obj,
                current_time=timedelta(seconds=self.connection.space_center.ut),
            )
            alarms[alarm.id] = alarm

        return alarms

    def _remove_all_alarms(self):
        """Kerbal Alarm Clock alarms do not get removed when returning to an earlier quick save,
        so this function deletes them manually."""

        alarm_objs = self.kac.alarms
        for alarm_obj in alarm_objs:
            alarm_obj.remove()

    add_alarm_parser = Cmd2ArgumentParser(
        epilog=f"Returns:\n{Alarm.model_json_schema()['title']}: {json.dumps(Alarm.model_json_schema()['properties'], indent=4)}"
    )
    add_alarm_parser.add_argument(
        "-name",
        type=str,
        required=True,
        help="Name of the alarm",
    )
    add_alarm_parser.add_argument(
        "-time",
        type=float,
        required=True,
        help="Universal time at which the alarm will trigger",
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
            name=args.name, time=args.time, description=args.description
        )

        self._cmd.poutput(f"New alarm created:\n{new_alarm.model_dump_json(indent=4)}")

    def add_alarm(self, name, time, description) -> Alarm:
        """Create a new alarm"""

        alarm_obj = self.kac.create_alarm(
            type=self.kac.AlarmType.raw,
            name=name,
            ut=time,
        )
        alarm_obj.notes = description
        alarm_obj.action = (
            self.kac.AlarmAction.message_only
        )  # TODO: might need custom logic to pass message to console app
        alarm_obj.vessel = self.vessel

        alarm = Alarm(alarm_obj)

        return alarm
