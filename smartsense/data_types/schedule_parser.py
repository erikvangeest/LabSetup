import json
from datetime import datetime
import inspect

class ScheduleParser:
    def __init__(self, heater_programs_module = None, pulse_program_module = None, mfc_program_module = None, logger = None):
        self.heater_programs_module = heater_programs_module
        self.pulse_programs_module = pulse_program_module
        self.mfc_programs_module = mfc_program_module
        self.logger = logger
    
    def check_file(self, filename) -> bool:
        valid = True
        schedule_frame = json.load(open(filename))
        # Check the frame type
        if schedule_frame["type"] != "schedule":
            self.log("ERROR", "Frame must be of type 'schedule'")
            valid = False
        # Check if repeat is enabled
        if schedule_frame["repeat"]:
            self.log("INFO", "Repeat is enabled")
        else:
            self.log("INFO", "Repeat is disabled")
        # Check each entry in the schedule (task/action/job)
        total_time_minutes = 0
        task_number = 1
        for task in schedule_frame["schedule"]:
            task_time = datetime.strptime(task["duration"], "%H:%M").time()
            self.log("INFO", f"Task {task_number} takes {task_time.hour} hours and {task_time.minute} minutes")
            total_time_minutes += task_time.hour * 60 + task_time.minute
            valid &= self.check_heater_program(task)
            valid &= self.check_pulse_program(task)
            valid &= self.check_mfc_program(task)
            task_number += 1
        self.log("SUCCESS", f"Duration of schedule is {total_time_minutes // 60} hours and {total_time_minutes % 60} minutes")
        return valid
    
    def check_heater_program(self, task) -> bool:
        valid = True
        # Check if the heater module is loaded
        if not self.heater_programs_module:
            self.log("WARNING", "Heater program definitions not found")
        else:
            heater_program = task["heater_program"]
            # Check if a heater program is given
            if heater_program:
                # Check if the heater program is known
                if hasattr(self.heater_programs_module, heater_program["name"]):
                    heater_program_check = getattr(self.heater_programs_module, heater_program["name"]).check_parameters
                    # Check the parameters
                    required_parameters = inspect.signature(heater_program_check).parameters.keys()
                    given_parameters = heater_program.get("parameters", {})
                    given_parameters["logger"] =  self.logger

                    missing_parameters = [param for param in required_parameters if param not in given_parameters]
                    extra_parameters = [param for param in given_parameters if param not in required_parameters]

                    if extra_parameters or missing_parameters:
                        if extra_parameters:
                            self.log("ERROR", f"Heater program given the following unknown parameters {extra_parameters}")
                            valid = False
                        if missing_parameters:
                            self.log("ERROR", f"Heater program missing the following parameters {missing_parameters}")
                            valid = False
                    else:
                        if heater_program_check(**given_parameters):
                            self.log("SUCCESS", "Heater program verified")
                else:
                    self.log("ERROR", "Heater program not supported by hardware")
                    valid = False
            else:
                self.log("INFO", "No heater program selected")
        return valid

    def check_pulse_program(self, task):
        valid = True
        # Check if the pulse module is loaded
        if not self.pulse_programs_module:
            self.log("WARNING", "Pulse program definitions not found")
        else:
            pulse_program = task["pulse_program"]
            # Check if a pulse program is given
            if pulse_program:
                # Check if the pulse program is known
                if hasattr(self.pulse_programs_module, pulse_program["name"]):
                    pulse_program_check = getattr(self.pulse_programs_module, pulse_program["name"]).check_parameters
                    # Check the parameters
                    required_parameters = inspect.signature(pulse_program_check).parameters.keys()
                    given_parameters = pulse_program.get("parameters", {})
                    given_parameters["logger"] = self.logger

                    missing_parameters = [param for param in required_parameters if param not in given_parameters]
                    extra_parameters = [param for param in given_parameters if param not in required_parameters]

                    if extra_parameters or missing_parameters:
                        if extra_parameters:
                            self.log("ERROR", f"Pulse program given the following unknown parameters {extra_parameters}")
                            valid = False
                        if missing_parameters:
                            self.log("ERROR", f"Pulse program missing the following parameters {missing_parameters}")
                            valid = False
                    else:
                        if pulse_program_check(**given_parameters):
                            self.log("SUCCESS", "Pulse program verified")
                else:
                    self.log("ERROR", "Pulse program not supported by hardware")
                    valid = False
            else:
                self.log("INFO", "No pulse program selected")
        return valid
    
    def check_mfc_program(self, task) -> bool:
        valid = True
        # Check if the mfc module is loaded
        if not self.mfc_programs_module:
            self.log("WARNING", "MFC program definitions not found")
        else:
            mfc_program = task["mfc_program"]
            # Check if an mfc program is given
            if mfc_program:
                # Check if the mfc program is known
                if hasattr(self.mfc_programs_module, mfc_program["name"]):
                    mfc_program_check = getattr(self.mfc_programs_module, mfc_program["name"]).check_parameters
                    # Check the parameters
                    required_parameters = inspect.signature(mfc_program_check).parameters.keys()
                    given_parameters = mfc_program.get("parameters", {})
                    given_parameters["logger"] = self.logger

                    missing_parameters = [param for param in required_parameters if param not in given_parameters]
                    extra_parameters = [param for param in given_parameters if param not in required_parameters]

                    if extra_parameters or missing_parameters:
                        if extra_parameters:
                            self.log("ERROR", f"MFC program given the following unknown parameters {extra_parameters}")
                            valid = False
                        if missing_parameters:
                            self.log("ERROR", f"MFC program missing the following parameters {missing_parameters}")
                            valid = False
                    else:
                        if mfc_program_check(**given_parameters):
                            self.log("SUCCESS", "MFC program verified")
                    
                else:
                    self.log("ERROR", "MFC program not supported by hardware")
                    valid = False
            else:
                self.log("INFO", "No MFC program selected")
        return valid
    
    def log(self, level: str, message: str):
        if (self.logger):
            self.logger.log(level, message)





