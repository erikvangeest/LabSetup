import serial
from time import sleep, time
from datetime import datetime
import csv
import os
import sys
import json
import random
import atexit
import re

from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient

# --------------------------------------------------------------------
# BASIC CONFIG
# --------------------------------------------------------------------
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 3600  # 1 hour in seconds
additional_stabilization = (
    time_hours * int(sys.argv[1]) if len(sys.argv) > 1 else 0
)

EBOX_UID_MFC = "MFC_LABSETUP"
EBOX_UID_VALVE = "VALVE_LABSETUP"
EBOX_SOFTWARE = "BURGERKING & WIJSVINGER INC. SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"

experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(
    open(r'C:\Users\smart\Scripts\Master codes\experiment_config.json')
)

logger = None

# MFC data client / frame buffer
database_mfc = MQTTClient(EBOX_UID_MFC)
database_mfc.connect()
atexit.register(database_mfc.disconnect)

frame_buffer_mfc = FrameBuffer(
    EBOX_UID_MFC,
    EBOX_SOFTWARE,
    SENSORHEAD_FIRMWARE,
    experiment_uid,
    list(experiment_config["receptors"].values()),
    logger,
)

# Valve data client / frame buffer
database_valve = MQTTClient(EBOX_UID_VALVE)
database_valve.connect()
atexit.register(database_valve.disconnect)

frame_buffer_valve = FrameBuffer(
    EBOX_UID_VALVE,
    EBOX_SOFTWARE,
    SENSORHEAD_FIRMWARE,
    experiment_uid,
    list(experiment_config["receptors"].values()),
    logger,
)

print('Eth MFC + valve script (no time drift) started')

# --------------------------------------------------------------------
# DEVICE CLASSES
# --------------------------------------------------------------------
class MassFlowController:
    def __init__(self, port, adress):
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1,
        )
        self.adress = adress
        self.response = ""

    def setValue(self, set_point):
        if self.ser.is_open:
            self.ser.write(f"*{self.adress} V 4 ={set_point}\r\n".encode())
        self.read_data()

    def mfc_mode(self, mode):
        if self.ser.is_open:
            self.ser.write(f"*{self.adress} V 1 ={mode}\r\n".encode())
        self.read_data()

    def mfc_read(self):
        if self.ser.is_open:
            self.ser.write(f"*{self.adress} F\r\n".encode())
        self.read_data()
        self.response = self.response.strip(' SCCM>')
        return self.response

    def read_data(self):
        sleep(0.1)
        if self.ser.in_waiting > 0:
            self.response = self.ser.readline().decode('utf-8')
            self.response = self.response.replace('\r', '')


class ValveController:
    """
    Controls the valve Arduino which listens for simple 'OPEN' / 'CLOSE' commands.
    The Arduino uses your sketch that prints 'READY' once on startup.
    """
    def __init__(self, port="COM20", baudrate=9600, timeout=1.0,
                 wait_ready=True, ready_timeout=10.0):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
        )
        if wait_ready:
            self._wait_for_ready(ready_timeout)

    def _wait_for_ready(self, ready_timeout: float):
        start = time()
        got_ready = False
        while time() - start < ready_timeout:
            line = self.ser.readline().decode(errors="ignore").strip()
            if line:
                print("Arduino:", line)
            if line.upper().startswith("READY"):
                got_ready = True
                print("Arduino valve controller READY")
                break
            sleep(0.1)
        if not got_ready:
            print("WARNING: No READY message received from Arduino valve controller.")

    def send_command(self, cmd: str):
        if not self.ser.is_open:
            return
        msg = cmd.strip() + "\n"
        self.ser.write(msg.encode())
        self.ser.flush()
        resp = self.ser.readline().decode(errors="ignore").strip()
        if resp:
            print("Arduino:", resp)

    def set_state(self, state: str):
        state = state.upper()
        if state == "OPEN":
            self.send_command("OPEN")
        elif state == "CLOSE":
            self.send_command("CLOSE")
        else:
            print(f"Unknown valve state '{state}', ignoring.")

    def close(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception as e:
                print(f"Error closing valve serial: {e}")


# --------------------------------------------------------------------
# DEVICE INSTANCES
# --------------------------------------------------------------------
MFC1 = MassFlowController(port="COM6", adress=11) # Ethyleen
MFC2 = MassFlowController(port="COM7", adress=12) # Lucht
valve = ValveController(port="COM4", baudrate=9600, wait_ready=True)

# --------------------------------------------------------------------
# CSV LOGGING SETUP
# --------------------------------------------------------------------
root_folder = (
    r'C:\Users\smart\Scripts'
    r'\Logs\MFC logs'
)

def create_new_folder_for_current_date():
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(root_folder, current_date)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def create_new_csv_file(folder_path):
    tstamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    csv_filename = os.path.join(folder_path, f"{tstamp}_MFC1+MFC2_log.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "MFC1 Value", "MFC2 Value"])
    return csv_filename

current_folder_path = create_new_folder_for_current_date()
csv_filename = create_new_csv_file(current_folder_path)

# --------------------------------------------------------------------
# MFC DATA ACCUMULATOR (FOR AWS)
# --------------------------------------------------------------------
mfc_data = {
    "MFC1": [],
    "MFC2": [],
    "timestamp": [],
}

send_interval_mfc = 120  # seconds (2 minutes)
last_send_time_mfc = time()

def read_mfc_data():
    ts = datetime.now().timestamp()
    MFC1val = MFC1.mfc_read()
    MFC2val = MFC2.mfc_read()

    # Keep only the part before the first space
    MFC1val = re.match(r'[^ ]*', MFC1val).group()
    MFC2val = re.match(r'[^ ]*', MFC2val).group()
    print(f"Read MFC data: timestamp={ts}, MFC1={MFC1val}, MFC2={MFC2val}")

    mfc_data["timestamp"].append(ts)
    mfc_data["MFC1"].append(float(MFC1val))
    mfc_data["MFC2"].append(float(MFC2val))
    print(f"Appended MFC data: timestamp={ts}, MFC1={MFC1val}, MFC2={MFC2val}")

def send_mfc_data_to_database():
    global mfc_data
    try:
        frame_buffer_mfc.generate_environmental_frame(
            sensorhead_name="SensorheadLS",
            start_time=datetime.now().timestamp(),
            measurement_data=mfc_data,
        )
        if frame_buffer_mfc.get_size() > 0:
            for frame in frame_buffer_mfc.get_frames():
                database_mfc.upload(frame.model_dump_json())
                sleep(0.1)
            frame_buffer_mfc.clear_frames()
            print("Uploaded MFC data to the database.")
        else:
            print("No MFC frames to upload.")
    except Exception as e:
        print(f"Failed to upload MFC data to the database: {e}")
    finally:
        mfc_data["MFC1"].clear()
        mfc_data["MFC2"].clear()
        mfc_data["timestamp"].clear()
        print("Cleared MFC data accumulator.")

def update_mfc_data():
    global last_send_time_mfc
    read_mfc_data()
    if time() - last_send_time_mfc >= send_interval_mfc:
        send_mfc_data_to_database()
        last_send_time_mfc = time()

# --------------------------------------------------------------------
# VALVE DATA ACCUMULATOR (FOR AWS)
# --------------------------------------------------------------------
valve_data = {
    "valve_1": [],
    "timestamp": [],
}

send_interval_valve = 120  # seconds (2 minutes)
last_send_time_valve = time()

def log_valve_state(state: str):
    """
    Log current valve state ('OPEN' or 'CLOSE') as 1 or 0.
    """
    state = state.upper()
    if state not in ("OPEN", "CLOSE"):
        print(f"Unknown valve state '{state}' in log_valve_state")
        return

    value = 1.0 if state == "OPEN" else 0.0
    ts = datetime.now().timestamp()
    valve_data["valve_1"].append(value)
    valve_data["timestamp"].append(ts)
    # print("Logged valve state:", state, "->", value, ts)

def send_valve_data_to_database():
    global valve_data
    try:
        if not valve_data["timestamp"]:
            return

        frame_buffer_valve.generate_environmental_frame(
            sensorhead_name="SensorheadLS",
            start_time=datetime.now().timestamp(),
            measurement_data=valve_data,
        )

        if frame_buffer_valve.get_size() > 0:
            for frame in frame_buffer_valve.get_frames():
                database_valve.upload(frame.model_dump_json())
                sleep(0.1)
            frame_buffer_valve.clear_frames()
            print("Uploaded valve data to the database.")
        else:
            print("No valve frames to upload.")
    except Exception as e:
        print(f"Failed to upload valve data to the database: {e}")
    finally:
        valve_data["valve_1"].clear()
        valve_data["timestamp"].clear()
        print("Cleared valve data accumulator.")

def send_valve_data_if_due():
    global last_send_time_valve
    if time() - last_send_time_valve >= send_interval_valve:
        send_valve_data_to_database()
        last_send_time_valve = time()

# --------------------------------------------------------------------
# ONE LOOP STEP (MFC + VALVE + LOGGING)
# --------------------------------------------------------------------
def perform_loop(loop_config):
    """
    Perform one [duration, MFC1, MFC2, valve] segment.

    loop_config keys:
      - 'duration'   : in hours
      - 'MFC1_value' : SCCM
      - 'MFC2_value' : SCCM
      - optional 'valve': 'OPEN' or 'CLOSE'
            If omitted, valve will be OPEN when MFC1_value > 0, else CLOSE.
    """
    MFC1value = loop_config['MFC1_value']
    MFC2value = loop_config['MFC2_value']
    duration = loop_config['duration'] * time_hours

    # Decide valve state: use explicit or infer from MFC1
    valve_state = loop_config.get(
        'valve',
        'OPEN' if MFC1value > 0 else 'CLOSE'
    ).upper()

    # Configure MFCs
    MFC1.setValue(MFC1value)
    MFC2.setValue(MFC2value)
    MFC1.mfc_mode(1)
    MFC2.mfc_mode(1)

    # Configure valve
    valve.set_state(valve_state)

    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"MFC1={MFC1value}, MFC2={MFC2value}, VALVE={valve_state}"
    )

    start_time = time()
    while time() - start_time < duration:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mfc1_val = MFC1.mfc_read()
        mfc2_val = MFC2.mfc_read()

        # CSV logging
        with open(csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp_str, mfc1_val, mfc2_val])

        # Update MFC data for DB
        update_mfc_data()

        # Log valve state and send if needed
        log_valve_state(valve_state)
        send_valve_data_if_due()

        # second sample within this 10-second cycle
        sleep(5)
        update_mfc_data()
        log_valve_state(valve_state)
        send_valve_data_if_due()
        sleep(5)

# --------------------------------------------------------------------
# LOOP SCHEDULE
# --------------------------------------------------------------------
# Pattern copied from your colleague's script, but now valve
# is automatically OPEN when MFC1 > 0, CLOSE when MFC1 == 0.
# Units are in ml/min
#loop_schedule = [
#    {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # baseline
#    {'duration': 1, 'MFC1_value': 2.5,  'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 5,    'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 10,   'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 20,   'MFC2_value': 100},
#    {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # final baseline
#]

# new schudule for 0.5% ethylene gas in tank
loop_schedule = [
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # baseline
     {'duration': 1, 'MFC1_value': 0.4,  'MFC2_value': 100}, # 20 ppm
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
     {'duration': 1, 'MFC1_value': 2.0,    'MFC2_value': 100}, # 100 ppm
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
     {'duration': 1, 'MFC1_value': 4.17,   'MFC2_value': 100}, # 200 ppm
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
     {'duration': 1, 'MFC1_value': 6.38,   'MFC2_value': 100}, # 300 ppm
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
     {'duration': 1, 'MFC1_value': 11.11,   'MFC2_value': 100}, # 500 ppm
     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # final baseline
 ]

# new schedule for 0.1% ethylene gas in tank
# loop_schedule = [
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # baseline
#     {'duration': 1, 'MFC1_value': 2.0,  'MFC2_value': 100}, # 20 ppm
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#     {'duration': 1, 'MFC1_value': 11.11,    'MFC2_value': 100}, # 100 ppm
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#     {'duration': 1, 'MFC1_value': 25.0,   'MFC2_value': 100}, # 200 ppm
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#     {'duration': 1, 'MFC1_value': 42.86,   'MFC2_value': 100}, # 300 ppm
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},
#     {'duration': 1, 'MFC1_value': 100,   'MFC2_value': 100}, # 500 ppm
#     {'duration': 1, 'MFC1_value': 0,    'MFC2_value': 100},  # final baseline
# ]


# --------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------
# Initial additional stabilization before starting the schedule
if additional_stabilization > 0:
    print(f"Additional stabilization: {additional_stabilization / time_hours:.2f} hours")
    sleep(additional_stabilization)

try:
    while True:
        for loop_config in loop_schedule:
            perform_loop(loop_config)

except KeyboardInterrupt:
    print("KeyboardInterrupt in Eth MFC + valve script. Flushing remaining data...")
    try:
        if mfc_data["MFC1"] or mfc_data["MFC2"] or mfc_data["timestamp"]:
            send_mfc_data_to_database()
    except Exception as e:
        print(f"Error flushing MFC data on exit: {e}")

    try:
        if valve_data["valve_1"] or valve_data["timestamp"]:
            send_valve_data_to_database()
    except Exception as e:
        print(f"Error flushing valve data on exit: {e}")

finally:
    try:
        valve.set_state("CLOSE")
    except Exception:
        pass
    try:
        valve.close()
    except Exception:
        pass
    print("Eth MFC + valve script stopped.")