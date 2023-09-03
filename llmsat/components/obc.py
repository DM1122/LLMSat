import json
from dataclasses import dataclass
from typing import Any
from pathlib import Path



class OBC:
    """Onboard computer"""
    def __init__(self):
        pass


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



