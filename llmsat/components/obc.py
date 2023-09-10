from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime


class OBC:
    """Onboard computer"""

    def __init__(self, alarm_manager: AlarmManager):
        self.alarm_manager = alarm_manager

    def get_spacecraft_properties(self) -> SpacecraftProperties:
        properties = {
            "mass [kg]": 4,
            "inertia_matrix [kg m^2]": {
                "XX": 1,
                "XY": 0,
                "XZ": 1,
                "YX": 0,
                "YY": 1,
                "YZ": 0,
                "ZX": 0,
                "ZY": 0,
                "ZZ": 1,
            },
        }

        return properties


if __name__ == "__main__":
    config = load_spacecraft_properties(SPACECRAFT_PROPERTIES)
