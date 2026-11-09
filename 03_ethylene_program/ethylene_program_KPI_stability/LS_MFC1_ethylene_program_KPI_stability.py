import serial
from time import sleep, time
from datetime import datetime
import csv, os
import sys
import json
import random
from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient
import atexit

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 3600  # normal = 3600
additional_stabilization = time_hours * int(sys.argv[1]) if len(sys.argv) > 1 else 0

EBOX_UID = "MFC_LABSETUP"
EBOX_SOFTWARE = "BURGERKING & WIJSVINGER INC. SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"
experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(open(r'C:\Users\User\Documents\Git Repository\Master codes\experiment_config.json'))

database = MQTTClient(EBOX_UID)
database.connect()
atexit.register(database.disconnect)
logger = None

frame_buffer = FrameBuffer(EBOX_UID, EBOX_SOFTWARE, SENSORHEAD_FIRMWARE, experiment_uid, list(experiment_config["receptors"].values()), logger)

print('Eth MFC script started')

class MassFlowController:
    def __init__(self, port, adress):
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1
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

MFC1 = MassFlowController(port="COM13", adress=11)
MFC2 = MassFlowController(port="COM14", adress=12)

root_folder = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\MFC logs'

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
csv_initialized = True

mfc_data = {
    "MFC1": [],
    "MFC2": [],
    "timestamp": []
}

send_interval = 120  # 2 minutes
last_send_time = time()

def read_mfc_data():
    ts = datetime.now().timestamp()
    MFC1val = MFC1.mfc_read()
    MFC2val = MFC2.mfc_read()
    
    mfc_data["timestamp"].append(ts)
    mfc_data["MFC1"].append(float(MFC1val))
    mfc_data["MFC2"].append(float(MFC2val))
    print(f"Appended MFC data: timestamp={ts}, MFC1={MFC1val}, MFC2={MFC2val}")

def send_accumulated_data_to_database():
    try:
        frame_buffer.generate_environmental_frame(
            sensorhead_name="SensorheadLS",
            start_time=datetime.now().timestamp(),
            measurement_data=mfc_data
        )
        if frame_buffer.get_size() > 0:
            for frame in frame_buffer.get_frames():
                database.upload(frame.model_dump_json())
                sleep(0.1)
            frame_buffer.clear_frames()
        else:
            print("No frames to upload.")
    except Exception as e:
        print(f"Failed to upload MFC data to the database: {e}")

    mfc_data["MFC1"].clear()
    mfc_data["MFC2"].clear()
    mfc_data["timestamp"].clear()
    print("Cleared MFC data.")

def update_mfc_data():
    global last_send_time
    read_mfc_data()
    if time() - last_send_time >= send_interval:
        send_accumulated_data_to_database()
        last_send_time = time()

# --- Perform one ON/OFF loop ---
def perform_loop(loop_config):
    MFC1value = loop_config['MFC1_value']
    MFC2value = loop_config['MFC2_value']
    duration = loop_config['duration'] * time_hours

    MFC1.setValue(MFC1value)
    MFC2.setValue(MFC2value)
    MFC1.mfc_mode(1)
    MFC2.mfc_mode(1)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MFC1={MFC1value}, MFC2={MFC2value}")

    start_time = time()
    while time() - start_time < duration:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mfc1_val = MFC1.mfc_read()
        mfc2_val = MFC2.mfc_read()

        with open(csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp_str, mfc1_val, mfc2_val])
        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)
        
# Loop pattern: [(duration_multiplier, MFC1_value, MFC2_value), ...]
loop_schedule = [
    {'duration': 0.8, 'MFC1_value': 0, 'MFC2_value': 100},
    {'duration': 1.2, 'MFC1_value': 2.5, 'MFC2_value': 100},
    {'duration': 0.8, 'MFC1_value': 0, 'MFC2_value': 100},
    {'duration': 1.2, 'MFC1_value': 5, 'MFC2_value': 100},
    {'duration': 0.8, 'MFC1_value': 0, 'MFC2_value': 100},
    {'duration': 1.2, 'MFC1_value': 10, 'MFC2_value': 100},
    {'duration': 0.8, 'MFC1_value': 0, 'MFC2_value': 100},
    {'duration': 1.2, 'MFC1_value': 20, 'MFC2_value': 100},
    {'duration': 1, 'MFC1_value': 0, 'MFC2_value': 100}
]

sleep(additional_stabilization)
try:
    while True:
        for loop_config in loop_schedule:
            perform_loop(loop_config)

except KeyboardInterrupt:
    if mfc_data["MFC1"] or mfc_data["MFC2"] or mfc_data["timestamp"]:
        send_accumulated_data_to_database()
    pass