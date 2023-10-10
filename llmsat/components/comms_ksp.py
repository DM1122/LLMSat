import krpc
from pydantic import BaseModel, validator

class CommunicationProperties(BaseModel):
    """Basic properties of the spacecraft"""

    can_communicate: bool


class Comms:

    def __init__(self, vessel):

        self.vessel = vessel

    def get_comm_properties(self):

        properties = CommunicationProperties(can_communicate=self.vessel.can_communicate)

