from time import time
from smartsense.sensorhead.sensorhead import Sensorhead

# Please Note: the class naming is unconventional,
# This is done to be in line with the json files

# Hardware limitations of the sensorhead hardware
MAX_TEMPERATURE = 125
MIN_TEMPERATURE = 0
# If shorter times than these a given a warning is shown (not an error)
RISE_TIME_MIN = 20
FALL_TIME_MIN = 120

class squarewave:
    def __init__(self, sensorhead: Sensorhead, temperature_low: int, temperature_high: int, time_low: int, time_high: int):
        self.sensorhead = sensorhead
        self.temperature_low = temperature_low
        self.temperature_high = temperature_high
        self.time_low = time_low
        self.time_high = time_high
        self.start_time = time()

    @classmethod
    def check_parameters(cls, logger, temperature_low: int, temperature_high: int, time_low: int, time_high: int):
        valid = True
        if (not check_temperature_limits(temperature_low)):
            valid = False
            log(logger, "ERROR", "temperature_low outside of range")
        if (not check_temperature_limits(temperature_high)):
            valid = False
            log(logger, "ERROR", "temperature_high outside of range")
        if (temperature_low > temperature_high):
            log(logger, "WARNING", "Lower temperature higher than high temperature")
        if (temperature_low == temperature_high):
            log(logger, "WARNING", "High and low temperature are equal")
        if (time_low < FALL_TIME_MIN):
            log(logger, "WARNING", "Low time is short, temperature might not be reached in time")
        if (time_high < RISE_TIME_MIN):
            log(logger, "WARNING", "High time is short, temperature might not be reached in time")
        return valid
    
    def update(self):
        # FIXME: Implementation always starts low, not actually defined
        if ((time() - self.start_time) % (self.time_low + self.time_high) < self.time_low):
            self.sensorhead.set_heater_targets(self.temperature_low)
        else:
            self.sensorhead.set_heater_targets(self.temperature_high)

class constant:
    def __init__(self, sensorhead: Sensorhead, temperature: int):
        self.sensorhead = sensorhead
        self.temperature = temperature
        self.last_set_time = 0

    @classmethod
    def check_parameters(cls, logger, temperature: int):
        valid = True
        if (not check_temperature_limits(temperature)):
            valid = False
            log(logger, "ERROR", "Temperature outside of range")
        return valid
    
    def update(self):
        if (time() - self.last_set_time >= 5):
            # Re-send the temperature every 5 seconds
            self.last_set_time = time()
            self.sensorhead.set_heater_targets(self.temperature)

def check_temperature_limits(temperature):
    return MIN_TEMPERATURE <= temperature and temperature <= MAX_TEMPERATURE

def log(logger, level: str, message: str):
    if (logger):
        logger.log(level, message)