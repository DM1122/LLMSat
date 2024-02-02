"""AlarmManager class."""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict

from cmd2 import CommandSet, with_argparser, with_default_category
from pydantic import BaseModel, Field, field_serializer

from llmsat.libs import utils


class Alarm(BaseModel):
    """An alarm"""

    id: str = Field(description="The unique identifier for the alarm")
    name: str = Field(description="Name of the alarm")
    description: str = Field(description="Description of the alarm")
    time: datetime = Field(description="Universal time at which the alarm will trigger")
    # margin: float = Field(
    #     description="The number of seconds before the event that the alarm will fire"
    # )
    obj: Any

    def __init__(self, alarm_obj):
        super().__init__(
            id=alarm_obj.id,
            name=alarm_obj.name,
            description=alarm_obj.notes,
            time=utils.ksp_ut_to_datetime(alarm_obj.time),
            # margin=alarm_obj.margin,
            obj=alarm_obj,
        ),

    # class Config:
    #     exclude = ["obj"]

    def get_remaining_time(
        self, current_time: datetime
    ) -> timedelta:  # alarm_obj.remaining is broken
        """Returns the timedelta between the trigger time and the current time."""
        return self.time - current_time

    @field_serializer("time")
    def serialize_dt(self, time: datetime, _info):
        return time.isoformat()

    def update_name(self, value):
        self.name = value
        self.obj.name = value


@with_default_category("AlarmManager")
class AlarmManager(CommandSet):
    """Functions for setting alarms."""

    TRIGGERED_STR = "(TRIGGERED)"

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AlarmManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection, remove_alarms_on_init=True):
        if AlarmManager._initialized:
            return
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel
        self.kac = self.connection.kerbal_alarm_clock

        if remove_alarms_on_init:
            self._remove_all_alarms()

        self.ut_stream = self.connection.add_stream(
            getattr, self.connection.space_center, "ut"
        )
        # Start the alarm monitoring in a separate thread
        self.alarm_thread = threading.Thread(target=self.monitor_alarms, daemon=True)
        self.alarm_thread.start()

        AlarmManager._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return AlarmManager(None, None)._cmd

    def do_get_alarms(self, _):
        """Get all alarms"""
        alarms = self.get_alarms()

        if not alarms:
            self._cmd.poutput("No alarms set")
            return

        # calculate remaining time for each alarm and store in a list of tuples
        alarms_with_remaining_time = [
            (
                alarm,
                alarm.get_remaining_time(
                    utils.ksp_ut_to_datetime(self.connection.space_center.ut)
                ),
            )
            for alarm in alarms.values()
        ]

        # Sort the alarms in ascending order by remaining time
        alarms_sorted = sorted(alarms_with_remaining_time, key=lambda x: x[1])

        alarms_formatted: dict[str, dict[str, str]] = {}
        for alarm, remaining_time in alarms_sorted:
            alarms_formatted[alarm.id] = alarm.model_dump(
                mode="json", exclude=["id", "obj"]
            )
            alarms_formatted[alarm.id]["remaining"] = str(remaining_time)

        self._cmd.poutput(json.dumps(alarms_formatted, indent=4))

    def get_alarms(self) -> Dict[str, Alarm]:
        """Get all alarms"""

        alarm_objs = self.kac.alarms
        alarms: Dict[str, Alarm] = {}
        for alarm_obj in alarm_objs:
            alarm = Alarm(alarm_obj)
            alarms[alarm.id] = alarm

        return alarms

    def _remove_all_alarms(self):
        """Kerbal Alarm Clock alarms do not get removed when returning to an earlier quick save,
        so this function deletes them manually."""

        alarm_objs = self.kac.alarms
        for alarm_obj in alarm_objs:
            alarm_obj.remove()

    add_alarm_parser = utils.CustomCmd2ArgumentParser(
        cmd_instance_method=_get_cmd_instance,
        epilog=f"Returns:\n{Alarm.model_json_schema()['title']}: {json.dumps(Alarm.model_json_schema()['properties'], indent=4)}",
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

        self._cmd.poutput(
            f"New alarm created:\n{new_alarm.model_dump_json(indent=4, exclude=['obj'])}"
        )

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
        alarm_obj.action = self.kac.AlarmAction.kill_warp
        alarm_obj.vessel = self.vessel

        alarm = Alarm(alarm_obj)

        return alarm

    def _on_alarm_trigger(self, alarm: Alarm):
        """Handle a triggered alarm"""

        self._cmd.async_alert(
            f"{utils.ksp_ut_to_datetime(self.connection.space_center.ut)}::AlarmManager:: Alarm triggered:\n{alarm.model_dump_json(exclude=['obj'],indent=4)}"
        )

    def monitor_alarms(self):
        """Async monitoring of alarms"""
        time.sleep(
            1
        )  # need to make sure no alarms are raised before cmd2 is fully initialized
        while True:
            current_time = utils.ksp_ut_to_datetime(self.ut_stream())

            alarms = self.get_alarms()
            for alarm in alarms.values():
                if (
                    alarm.get_remaining_time(current_time) <= timedelta(0)
                    and AlarmManager.TRIGGERED_STR not in alarm.name
                ):
                    # alarm has triggered
                    self._on_alarm_trigger(alarm)
                    alarm.update_name(alarm.name + f" {AlarmManager.TRIGGERED_STR}")
