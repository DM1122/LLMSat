import krpc


class ADCS:

    def __init__(self, vessel):

        self.vessel = vessel

    def get_total_electric_charge(self) -> float:
