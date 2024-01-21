"""SpacecraftManager class."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List

from cmd2 import Cmd2ArgumentParser, CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field

from llmsat.libs import utils


class Alarm(BaseModel):
    """An alarm"""

    name: str = Field(description="Name of the alarm")
    description: str = Field(description="Description of the alarm")
    time: datetime = Field(description="Universal time at which the alarm will trigger")

    def __init__(self, alarm_obj):
        super().__init__(
            name=alarm_obj.name,
            description=alarm_obj.notes,
            time=utils.epoch + timedelta(seconds=alarm_obj.time),
        ),

    def get_remaining_time(self, current_time: datetime) -> timedelta:
        """Returns the timedelta between the trigger time and the current time."""
        return self.time - current_time


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

    def do_get_alarms(self, _):
        """Get all alarms"""
        alarms = self.get_alarms()

        if not alarms:
            self._cmd.poutput("No alarms have been set")
            return

        # Calculate remaining time for each alarm and store in a list of tuples
        alarms_with_remaining_time = [
            (alarm, alarm.get_remaining_time(utils.get_ut_time(self.connection)))
            for alarm in alarms.values()
        ]

        # Sort the alarms in ascending order by remaining time
        alarms_sorted = sorted(alarms_with_remaining_time, key=lambda x: x[1])

        # Format the sorted alarms into a dictionary of dictionaries
        alarms_formatted = {
            alarm.name: {
                "time": alarm.time.isoformat(),
                "remaining": str(remaining),
                "description": alarm.description,
            }
            for alarm, remaining in alarms_sorted
        }

        self._cmd.poutput(json.dumps(alarms_formatted, indent=4))

    def get_alarms(self) -> Dict[str, Alarm]:
        """Get all alarms"""

        alarm_objs = self.kac.alarms
        alarms = {}
        for alarm_obj in alarm_objs:
            alarm = Alarm(alarm_obj)
            alarms[alarm.name] = alarm

        return alarms

    def do_delete_alarm(self):
        pass

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
        type=str,
        required=True,
        help="Universal time at which the alarm will trigger in the format YYYY-MM-DDTHH:MM:SS",
    )
    add_alarm_parser.add_argument(
        "-desc",
        type=str,
        required=False,
        help="Description for the alarm",
    )

    @with_argparser(add_alarm_parser)
    def do_add_alarm(self, args):
        """Create a new alarm to trigger at a given universal time"""

        try:
            time = datetime.strptime(args.time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            self._cmd.perror(
                f"Invalid time format '{args.time}'. Must be YYYY-MM-DDTHH:MM:SS."
            )
            return

        try:
            new_alarm = self.add_alarm(name=args.name, time=time, description=args.desc)
        except ValueError as e:
            self._cmd.perror(e)
            return

        self._cmd.poutput(f"New alarm created:\n{new_alarm.model_dump_json(indent=4)}")

    def add_alarm(self, name, time: datetime, description) -> Alarm:
        """Create a new alarm to trigger at a given universal time"""

        alarms = self.get_alarms()
        if name in alarms:
            raise ValueError(f"An alarm with name '{name}' already exists")

        ut = (time - utils.epoch).total_seconds()

        alarm_obj = self.kac.create_alarm(
            type=self.kac.AlarmType.raw,
            name=name,
            ut=ut,
        )
        alarm_obj.notes = description if description is not None else ""
        alarm_obj.action = (
            self.kac.AlarmAction.message_only
        )  # TODO: might need custom logic to pass message to console app
        alarm_obj.vessel = self.vessel

        alarm = Alarm(alarm_obj)

        return alarm
