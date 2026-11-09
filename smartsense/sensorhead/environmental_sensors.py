from time import time
from smartsense.sensorhead.sensorhead import Sensorhead

class EnvironmentalSensors:
    def __init__(self, sensorhead: Sensorhead, measurement_delay: float, measurements_per_frame: int):
        self.sensorhead = sensorhead
        self.measurement_delay = measurement_delay
        self.measurements_per_frame = measurements_per_frame
        self.start_time = time()
        self.clear_data()

    def clear_data(self):
        self.data = {
            "time": [],
            "temperature_1": [],
            "humidity_1": [],
            "temperature_2": [],
            "humidity_2": [],
            "temperature_3": [],
            "humidity_3": [],
            "pressure_3": [],
            "voc_3": []
        }
        self.start_time = time()
        self.measurements_completed = 0
        self.last_measurement_time = 0
    
    def get_data(self):
        data = self.data
        self.clear_data()
        return data
    
    def update(self):
        if (time() - self.last_measurement_time >= self.measurement_delay):
            self.last_measurement_time = time()
            #data = self.sensorhead_manager.get_full_environmental(self.sensorhead_name)
            data = self.sensorhead.get_full_environmental()
            self.data["time"].append(time() - self.start_time)
            self.data["temperature_1"].append(data[0])
            self.data["humidity_1"].append(data[1])
            self.data["temperature_2"].append(data[2])
            self.data["humidity_2"].append(data[3])
            self.data["temperature_3"].append(data[4])
            self.data["humidity_3"].append(data[5])
            self.data["pressure_3"].append(data[6])
            self.data["voc_3"].append(data[7])
            self.measurements_completed += 1
        if (self.measurements_completed >= self.measurements_per_frame):
            return True
        return False