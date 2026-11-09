from typing import Dict
from time import time
import random

from pydantic import BaseModel, Field

class ExperimentFrame(BaseModel):
    timestamp: int = Field(default_factory=lambda: int(time()))
    uid: str = Field(default_factory=lambda: "%032x" % random.getrandbits(128))
    type: str = "experiment"
    frame_version: str = "0.8"
    name: str
    version: str
    schedule_uid: str
    start_time: str
    receptors: Dict[str, str]
    note: str
