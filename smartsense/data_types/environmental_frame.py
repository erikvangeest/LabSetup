from typing import Dict, List, Union
from time import time
import random

from pydantic import BaseModel, Field

class EnvironmentalFrame(BaseModel):
    timestamp: int = Field(default_factory=lambda: int(time()))
    uid: str = Field(default_factory=lambda: "%032x" % random.getrandbits(128))
    type: str = "environmental"
    frame_version: str = "0.1"
    source: Dict[str, Union[str, Dict[str, Union[str, int, float]]]]
    experiment_uid: str
    measurement: Dict[str, List[float]]
