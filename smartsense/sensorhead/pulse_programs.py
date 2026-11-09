from time import time
from smartsense.sensorhead.sensorhead import Sensorhead

# Please Note: the class naming is unconventional,
# This is done to be in line with the json files

class pulse_program_base:
    def __init__(self, sensorhead: Sensorhead):
        self.sensorhead = sensorhead
        self.start_time = time()
        self.clear_data()
    
    def clear_data(self):
        self.data = {
            "time": [],
            "voltage": [],
            "receptor_1": [],
            "receptor_2": [],
            "receptor_3": [],
            "receptor_4": [],
            "temperature": []
        }
        self.start_time = time()
    
    def get_data(self):
        data = self.data
        self.clear_data()
        return data


class ramp_up_down(pulse_program_base):
    def __init__(self, sensorhead: Sensorhead, voltage_min: float, voltage_max: float, voltage_step: float, time_step: float):
        super().__init__(sensorhead)
        self.voltage_min = voltage_min
        self.voltage_max = voltage_max
        self.voltage_step = voltage_step
        self.time_step = time_step
        self.gate_voltage = 0
        self.direction = True
    
    def clear_data(self):
        super().clear_data()
        self.last_measurement_time = 0
    
    @classmethod
    def check_parameters(cls, logger, voltage_min: float, voltage_max: float, voltage_step: float, time_step: float):
        valid = True
        if (not check_gate_limits(voltage_min)):
            valid = False
            log(logger, "ERROR", "voltage_min outside of range")
        if (not check_gate_limits(voltage_max)):
            valid = False
            log(logger, "ERROR", "voltage_max outside of range")
        if (voltage_min == voltage_max):
            log(logger, "WARNING", "Min and max voltage are equal")
        elif (voltage_max < voltage_min):
            valid = False
            log(logger, "ERROR", "Min voltage higher than max voltage")
        else:
            if (voltage_step > voltage_max - voltage_min):
                valid = False
                log(logger, "ERROR", "Voltage step bigger than voltage range")
        if (time_step < MIN_GATE_DELAY):
            log(logger, "WARNING", "Time step too small, measurements could be stale")
        return valid
    
    def update(self):
        if (time() - self.last_measurement_time >= self.time_step):
            self.last_measurement_time = time()
            measurement = self.sensorhead.get_full_measurement(True)

            self.data["time"].append(time() - self.start_time)
            self.data["voltage"].append(self.gate_voltage)
            self.data["temperature"].append(measurement[16:20])

            for receptor in range (1, 5):
                self.data[f"receptor_{receptor}"].append(measurement[(receptor - 1) * 4:(receptor - 1) * 4 + 4])
            
            if (self.direction):
                self.gate_voltage += self.voltage_step
                if (self.gate_voltage >= self.voltage_max):
                    self.direction = False
            else:
                self.gate_voltage -= self.voltage_step
                if (self.gate_voltage <= self.voltage_min):
                    self.direction = True
                    self.gate_voltage = self.voltage_min
                    # Signal back to the main application that the pulse has finished
                    return True
            self.sensorhead.set_gate_voltage(self.gate_voltage)
        return False

class constant(pulse_program_base):
    def __init__(self, sensorhead: Sensorhead, gate_voltage: float, measurement_delay: float, measurements_per_frame: int):
        super().__init__(sensorhead)
        self.gate_voltage = gate_voltage
        self.measurement_delay = measurement_delay
        self.measurements_per_frame = measurements_per_frame
    
    def clear_data(self):
        self.measurements = 0
        self.last_measurement_time = 0
        super().clear_data()
    
    @classmethod
    def check_parameters(cls, logger, gate_voltage: float, measurement_delay: float, measurements_per_frame: int):
        valid = True
        if (not check_gate_limits(gate_voltage)):
            valid = False
            log(logger, "ERROR", "gate_voltage outside of range")
        if (measurement_delay < MIN_GATE_DELAY):
            log(logger, "WARNING", "Time step too small, measurements could be stale")
        if (measurements_per_frame < 1):
            valid = False
            log(logger, "ERROR", "Measurements per frame must be more than 0")
        return valid
    
    def update(self):
        if (time() - self.last_measurement_time >= self.measurement_delay):
            self.last_measurement_time = time()
            measurement = self.sensorhead.get_full_measurement(True)

            self.data["time"].append(time() - self.start_time)
            self.data["voltage"].append(self.gate_voltage)
            self.data["temperature"].append(measurement[16:20])

            for receptor in range (1, 5):
                self.data[f"receptor_{receptor}"].append(measurement[(receptor - 1) * 4:(receptor - 1) * 4 + 4])
            
            self.measurements += 1

            if (self.measurements >= self.measurements_per_frame):
                return True
            self.sensorhead.set_gate_voltage(self.gate_voltage)
        return False


# Hardware limitations of the sensorhead hardware
MAX_GATE_VOLTAGE = 45.0
MIN_GATE_VOLTAGE = 0.0
# If shorter time than this a given a warning is shown (not an error)
# The minimum delay required for each ADC channel to do a reading (after setting a new gate voltage)
MIN_GATE_DELAY = 0.08    #TODO determine minimal value

def check_gate_limits(voltage):
    return MIN_GATE_VOLTAGE <= voltage and voltage <= MAX_GATE_VOLTAGE

def log(logger, level: str, message: str):
    if (logger):
        logger.log(level, message)
