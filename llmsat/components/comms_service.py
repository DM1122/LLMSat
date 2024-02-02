"""CommunicationService class."""

import json
from datetime import datetime
from pathlib import Path

from cmd2 import CommandSet, with_argparser, with_default_category
from pydantic import BaseModel

from llmsat.libs import utils

COMM_LOG_PATH = Path("disk/comm_log.json")


class CommMessage(BaseModel):
    timestamp: datetime
    fromm: str
    to: str
    message: str


@with_default_category("CommunicationService")
class CommunicationService(CommandSet):
    """Functions for orbit determination."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommunicationService, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        if CommunicationService._initialized:
            return
        super().__init__()
        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

        CommunicationService._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return CommunicationService()._cmd

    send_message_parser = utils.CustomCmd2ArgumentParser(
        _get_cmd_instance,
    )
    send_message_parser.add_argument(
        "-message",
        type=str,
        required=True,
        help="Message content",
    )

    @with_argparser(send_message_parser)
    def do_send_message(self, args):
        """Send a message to mission control"""

        message = CommMessage(
            timestamp=utils.ksp_ut_to_datetime(self.connection.space_center.ut),
            fromm=self.vessel.name,
            to="MissionControl",
            message=args.message,
        )
        self.send_message(message)

        self._cmd.poutput("Message sent")

    def send_message(self, message: CommMessage) -> CommMessage:
        """Send a message to mission control"""

        with open(COMM_LOG_PATH, "r") as file:
            data = json.load(file)

        messages = [CommMessage(**entry) for entry in data]

        messages.append(message)

        messages_serial = [message.model_dump(mode="json") for message in messages]
        with open(COMM_LOG_PATH, "w") as file:
            json.dump(messages_serial, file, indent=4)

        return message
