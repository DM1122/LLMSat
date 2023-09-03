class Battery:
    def __init__(self, capacity):
        self.capacity = capacity
        self.charge = capacity  # Initial charge

    def charge_battery(self, sun_view_factor, delta_t):
        charging_rate = (
            ...
        )  # Define based on your satellite's solar panels and sun view factor
        self.charge += charging_rate * sun_view_factor * delta_t
        if self.charge > self.capacity:
            self.charge = self.capacity

    def discharge_battery(self, power_draw, delta_t):
        self.charge -= power_draw * delta_t
        if self.charge < 0:
            self.charge = 0
