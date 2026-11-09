from typing import Dict, List
from time import time
import random

from pydantic import BaseModel, Field

class ScheduleFrame(BaseModel):
    timestamp: int = Field(default_factory=lambda: int(time()))
    uid: str = Field(default_factory=lambda: "%032x" % random.getrandbits(128))
    type: str = "schedule"
    frame_version: str = "0.5"
    name: str
    version: str
    start_time: str
    repeat: bool
    schedule: List[Dict[str, int|None|Dict[str, str|Dict[str, int|float]]]]
