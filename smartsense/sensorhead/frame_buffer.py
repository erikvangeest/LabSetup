from typing import Dict, List, Union

from smartsense.data_types.measurement_frame import MeasurementFrame
from smartsense.data_types.experiment_frame import ExperimentFrame
from smartsense.data_types.environmental_frame import EnvironmentalFrame

class FrameBuffer:
    def __init__(self, ebx_uid: str, ebox_software: str, sensorhead_firmware: str, experiment_uid: str, receptor_uids: List[str], logger=None):
        self.ebox_uid = ebx_uid
        self.ebox_software = ebox_software
        self.sensorhead_firmware = sensorhead_firmware
        self.experiment_uid = experiment_uid
        self.receptor_uids = receptor_uids
        self.logger = logger
        self.frames: List[MeasurementFrame | ExperimentFrame | EnvironmentalFrame] = []

    def get_size(self) -> int:
        return len(self.frames)

    def get_frames(self) -> List[Union[MeasurementFrame, ExperimentFrame, EnvironmentalFrame]]:
        return self.frames
    
    def clear_frames(self) -> None:
        self.frames = []

    def generate_environmental_frame(self, sensorhead_name: str, start_time: float, measurement_data: Dict[str, List[float]]) -> None:
        self.frames.append(EnvironmentalFrame(
            timestamp = int(start_time),
            source = {
                "type": "ebox",
                "data": {
                    "ebox_uid": self.ebox_uid,
                    "ebox_software": self.ebox_software,
                    "sensorhead_uid": sensorhead_name,
                    "sensorhead_firmware": self.sensorhead_firmware
                }
            },
            experiment_uid = self.experiment_uid,
            measurement = measurement_data
        ))
        self.log_frame(self.frames[-1])
    
    def generate_measurement_frames(self, sensorhead_name: str, receptor: int, start_time: float, measurement_data: Dict[str, List[float]]) -> None:
        self.frames.append(MeasurementFrame(
            timestamp = int(start_time),
            source = {
                "type": "ebox",
                "data": {
                    "ebox_uid": self.ebox_uid,
                    "ebox_software": self.ebox_software,
                    "sensorhead_uid": sensorhead_name,
                    "sensorhead_firmware": self.sensorhead_firmware,
                    "slot_index": receptor,
                    "receptor_uid": self.receptor_uids[receptor - 1]
                }
            },
            experiment_uid = self.experiment_uid,
            measurement = measurement_data
        ))
        self.log_frame(self.frames[-1])
    
    def generate_experiment_frame(self, name: str, version: str, schedule_uid: str, start_time: str, receptors: Dict[str, str], note: str) -> None:
        self.frames.append(ExperimentFrame(
            uid = self.experiment_uid,
            name = name,
            version = version,
            schedule_uid = schedule_uid,
            start_time = start_time,
            receptors = receptors,
            note = note
        ))
        self.log_frame(self.frames[-1])

    def log_frame(self, frame: Union[MeasurementFrame, ExperimentFrame, EnvironmentalFrame]) -> None:
        if self.logger:
            for field in frame:
                if field[0] == "measurement":
                    for key, value in field[1].items():
                        self.logger.trace(f"{key}: {value}")
                else:
                    self.logger.trace(field)
                