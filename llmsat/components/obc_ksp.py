import krpc
from pydantic import BaseModel, validator
from pathlib import Path
import numpy as np


class SpacecraftProperties(BaseModel):
    """Basic properties of the spacecraft"""

    name: str
    description: str
    type: str
    situation: str
    met: float
    biome: str
    mass: float
    dry_mass: float


class OBC:
    def __init__(self, vessel):
        self.vessel = vessel

    def get_spacecraft_properties(self) -> SpacecraftProperties:
        properties = SpacecraftProperties(
            name=self.vessel.name,
            description="A description",
            type=str(self.vessel.type),
            situation=str(self.vessel.situation),
            met=self.vessel.met,
            biome=self.vessel.biome,
            mass=self.vessel.mass,
            dry_mass=self.vessel.dry_mass,
        )

        return properties
