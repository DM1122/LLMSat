import astropy.units as unit
from pydantic import BaseModel


class CommunicationProperties(BaseModel):
    """Basic properties of the spacecraft"""

    can_communicate: bool


class Comms:
    def __init__(self, vessel):
        self.vessel = vessel

    # def get_comm_properties(self):

    #     properties = CommunicationProperties(can_communicate=self.vessel.can_communicate)

    def can_communicate(self) -> bool:
        """Whether the vessel can communicate with mission control."""

        return self.vessel.comms.can_communicate

    def can_transmit_science(self) -> bool:
        """Whether the vessel can transmit science data to mission control."""

        return self.vessel.comms.can_transmit_science

    def get_signal_strength(self) -> float:
        """Signal strength to mission control"""

        return self.vessel.comms.signal_strength

    def get_signal_delay(self) -> unit.Quantity[unit.s]:
        """Signal delay to mission control"""

        return self.vessel.comms.signal_delay * unit.s

    def get_power_draw(self) -> float:
        """Combined power draw of all active antennae on the vessel"""

        return self.vessel.comms.power

    def get_antenna_states(self):
        "Returns whether all antennas on the vessel are deployed"

        deployed = self.vessel.control.antennas

        return deployed

    def set_antenna_states(self, state: bool) -> bool:
        "Sets the deployment state of all antennas"

        self.vessel.control.antennas = state

        return True

    def get_antennas(self):
        """A list of all antennas in the vessel."""
        return self.vessel.parts.antennas
