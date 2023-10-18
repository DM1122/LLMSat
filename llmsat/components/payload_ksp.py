import krpc
from pydantic import BaseModel, validator
import astropy.units as unit


class PayloadManager:
    def __init__(self, vessel):
        self.vessel = vessel
