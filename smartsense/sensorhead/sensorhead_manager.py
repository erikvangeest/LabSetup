from time import time

from pymodbus.exceptions import ModbusIOException, ConnectionException, NotImplementedException

from smartsense.sensorhead.sensorhead import Sensorhead
from smartsense.sensorhead.modbus_client import ModbusClient
import smartsense.sensorhead.heater_programs as heater_programs
import smartsense.sensorhead.pulse_programs as pulse_programs
from smartsense.sensorhead.environmental_sensors import EnvironmentalSensors
from smartsense.sensorhead.frame_buffer import FrameBuffer

CONNECTION_RETRY_ATTEMPTS = 10
CONNECTION_RETRY_TIMER = 2

class SensorheadManager:
    def __init__(self, modbus_client: ModbusClient, frame_buffer: FrameBuffer, name: str, address: int = 1, logger = None):
        self.frame_buffer = frame_buffer
        self.name = name
        self.sensorhead = Sensorhead(modbus_client, address)
        self.logger = logger
        self.led_state = False
        self.heater_program = None
        self.pulse_program = None
        self.environmental_program = None
    
    def start(self):
        self.alive = True
        self.connected = False
        self.connection_retries = 0
        self.retry_timer = 0
        self.update()
    
    def set_retry_timer(self):
        self.connection_retries += 1
        self.retry_timer = time() + CONNECTION_RETRY_TIMER
    
    def set_heater_program(self, heater_program_name: str | None, **heater_program_parameters: int):
        if heater_program_name:
            self.heater_program = getattr(heater_programs, heater_program_name)(self.sensorhead, **heater_program_parameters)
        else:
            self.heater_program = None
            # Turn the heaters off when no heater program is specified
            self.sensorhead.set_heater_targets(0)
    
    def set_pulse_program(self, pulse_program_name: str | None, **pulse_program_parameters: int):
        if pulse_program_name:
            self.pulse_program = getattr(pulse_programs, pulse_program_name)(self.sensorhead, **pulse_program_parameters)
        else:
            self.pulse_program = None
            # Turn the gate voltage off when no pulse program is specified
            self.sensorhead.set_gate_voltage(0.0)
    
    def set_environmental(self, delay: float, measurements_per_frame: int):
        self.environmental_program = EnvironmentalSensors(self.sensorhead, delay, measurements_per_frame)

    def update(self):
        # This function is just a wrapper for the actual update function
        if not self.alive:
            return
        if self.connected:
            try:
                self.internal_update()
            except (ModbusIOException, ConnectionException):
                # Connection lost
                self.connected = False
                self.log("WARNING", f"Connection to {self.name} lost")
                self.set_retry_timer()
            except NotImplementedException:
                # Sensorhead most likely in bootloader
                self.connected = False
                self.log("WARNING", f"Connection to {self.name} lost, might be in bootloader")
                self.set_retry_timer()
        else:
            if (time() > self.retry_timer):
                try:
                    self.sensorhead.set_high_voltage(True)
                    # Connected again
                    self.connected = True
                    self.connection_retries = 0
                    self.log("SUCCESS", f"Connection to {self.name} established")
                except (ModbusIOException, ConnectionException):
                    self.log("INFO", f"Connection to {self.name} failed")
                    self.set_retry_timer()
                except NotImplementedException:
                    self.log("INFO", f"Connection to {self.name} failed, might be in bootloader")
                    self.set_retry_timer()
                if self.connection_retries > CONNECTION_RETRY_ATTEMPTS:
                    self.log("ERROR", f"Connection to {self.name} closed after {CONNECTION_RETRY_ATTEMPTS} retries")
                    self.alive = False

    def internal_update(self):
        # This is the actual update function
        # Blink the LED
        if bool(int(time() * 2) % 2) != self.led_state:
            self.led_state = not self.led_state
            self.sensorhead.set_led(1, self.led_state)
        
        if self.heater_program:
            self.heater_program.update()

        if self.pulse_program:
            if self.pulse_program.update():
                self.log("INFO", f"{self.name} Finished pulse program")
                data = self.pulse_program.get_data()
                for receptor in range(1, 5):
                    measurement = {
                        "time": data["time"],
                        "voltage": data["voltage"],
                        "resistance_1": [e[0] for e in data[f"receptor_{receptor}"]],
                        "resistance_2": [e[1] for e in data[f"receptor_{receptor}"]],
                        "resistance_3": [e[2] for e in data[f"receptor_{receptor}"]],
                        "resistance_4": [e[3] for e in data[f"receptor_{receptor}"]],
                        "temperature": [t[receptor - 1] for t in data["temperature"]]
                    }
                    self.frame_buffer.generate_measurement_frames(self.name, receptor, self.pulse_program.start_time, measurement)
        
        if self.environmental_program:
            if self.environmental_program.update():
                self.log("INFO", f"{self.name} Finished environmental program")
                data = self.environmental_program.get_data()
                measurement = {
                        "time": data["time"],
                        "temperature_1": data["temperature_1"],
                        "humidity_1": data["humidity_1"],
                        "temperature_2": data["temperature_2"],
                        "humidity_2": data["humidity_2"],
                        "temperature_3": data["temperature_3"],
                        "humidity_3": data["humidity_3"],
                        "pressure_3": data["pressure_3"],
                        "voc_3": data["voc_3"]
                    }
                self.frame_buffer.generate_environmental_frame(self.name, self.environmental_program.start_time, measurement)
    
    
    def shutdown(self):
        if self.connected:
            self.sensorhead.set_heater_targets(0)
            self.sensorhead.set_gate_voltage(0.0)
            self.sensorhead.set_high_voltage(False)
            self.sensorhead.set_led(1, False)
            self.log("SUCCESS", f"{self.name} shutdown")

    def log(self, level: str, message: str):
        if (self.logger):
            self.logger.log(level, message)
