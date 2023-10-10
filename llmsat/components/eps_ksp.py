# import krpc

# conn = krpc.connect(name="Hello World")
# vessel = conn.space_center.active_vessel
# print(vessel.name)

import krpc


class EPS:
    """
    A class that represents the Electrical Power System (EPS) of a satellite in KSP.

    Attributes:
        vessel (krpc.client.services.space_center.Vessel): The active vessel/satellite.
    """

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
