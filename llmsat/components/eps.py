import krpc


class EPS:
    def __init__(self, vessel):
        """
        Initializes an EPS object using the kRPC connection.

        """
        self.vessel = vessel

    def get_total_electric_charge(self) -> float:
        """
        Returns the total amount of electric charge available in the vessel.

        Returns:
            float: Total electric charge in the vessel.
        """
        return self.vessel.resources.amount("ElectricCharge")

    def get_max_electric_charge(self) -> float:
        """
        Returns the maximum amount of electric charge that can be stored in the vessel.

        Returns:
            float: Maximum electric charge the vessel can hold.
        """
        return self.vessel.resources.max("ElectricCharge")

    def get_percentage_electric_charge(self) -> float:
        """
        Returns the percentage of electric charge remaining in the vessel.

        Returns:
            float: Percentage of electric charge remaining.
        """
        return (self.get_total_electric_charge() / self.get_max_electric_charge()) * 100

    def get_solar_panel_states(self) -> bool:
        """Returns whether all solar panels on the vessel are deployed"""

        return self.vessel.control.solar_panels

    def set_solar_panel_states(self, state: bool) -> bool:
        """Sets the deployment state of all solar panels"""

        self.vessel.control.solar_panels = state

        return True
