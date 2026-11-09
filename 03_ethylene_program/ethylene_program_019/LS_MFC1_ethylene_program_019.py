import serial
from time import sleep, strftime, localtime, time
import csv
import os
import sys
from datetime import datetime
import json
import random
import numpy as np
from matplotlib import pyplot as plt
from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 1800   #normal = 3600
additional_stabilization = time_hours * int(sys.argv[1]) if len(sys.argv) > 1 else 0

EBOX_UID = "MFC_LABSETUP"
EBOX_SOFTWARE = "BURGERKING & WIJSVINGER INC. SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"
experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(open(r'C:\Users\User\Documents\Git Repository\Master codes\experiment_config.json'))

database = MQTTClient(EBOX_UID)
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

    def send_command(self):
        if self.ser.is_open:
            self.ser.write(f"*{self.adress} V 1 =1\r\n".encode())
        self.read_data()

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


duration1 = additional_stabilization + 0.8 * time_hours
start_time1 = time()

MFC1value = 0 ### CHANGED FROM 0 TO 20
MFC2value = 100
MFC1.setValue(MFC1value)
MFC2.setValue(MFC2value)
MFC1.mfc_mode(1)
MFC2.mfc_mode(1)
print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

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
            database.connect()
            for frame in frame_buffer.get_frames():
                database.upload(frame.model_dump_json())
                sleep(0.1)
            frame_buffer.clear_frames()
            database.disconnect()
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
    # Read MFC data (one reading per call)
    read_mfc_data()

    # Check if it's time to send data to the database
    if time() - last_send_time >= send_interval:
        send_accumulated_data_to_database()
        last_send_time = time()

try:
    # For each of your duration loops, we do:
    # 1. Perform CSV logging
    # 2. Call update_mfc_data() immediately (first MFC read)
    # 3. sleep(5), call update_mfc_data() again (second MFC read)
    # 4. sleep(5) -> total 10 seconds per iteration with 2 reads at 5-second intervals

    # LOOP 1
    while time() - start_time1 < duration1:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        # First MFC read/update
        update_mfc_data()

        # Wait 5 seconds
        sleep(5)

        # Second MFC read/update at 5-second interval
        update_mfc_data()

        # Another 5 seconds to complete the 10-second cycle
        sleep(5)

    # LOOP 2
    duration2 = 1.2 * time_hours
    start_time2 = time()
    MFC1value = 2.5
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time2 < duration2:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 3
    duration3 = 0.8 * time_hours
    start_time3 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time3 < duration3:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 4
    duration4 = 1.2 * time_hours
    start_time4 = time()
    MFC1value = 5
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time4 < duration4:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 5
    duration5 = 0.8 * time_hours
    start_time5 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time5 < duration5:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 6
    duration6 = 1.2 * time_hours
    start_time6 = time()
    MFC1value = 10
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time6 < duration6:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 7
    duration7 = 0.8 * time_hours
    start_time7 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time7 < duration7:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 8
    duration8 = 1.2 * time_hours
    start_time8 = time()
    MFC1value = 20
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time8 < duration8:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 9: STABILIZE for humidity correction = 4 hours
    
    duration9 = 3.8 * time_hours
    start_time9 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time9 < duration9:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 10: 
    
    duration10 = 1.2 * time_hours
    start_time10 = time()
    MFC1value = 2.5
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time10 < duration10:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 11
    duration11 = 0.8 * time_hours
    start_time11 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time11 < duration11:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 12
    duration12 = 1.2 * time_hours
    start_time12 = time()
    MFC1value = 5
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time12 < duration12:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 13
    duration13 = 0.8 * time_hours
    start_time13 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time13 < duration13:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 14
    duration14 = 1.2 * time_hours
    start_time14 = time()
    MFC1value = 10
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time14 < duration14:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 15
    duration15 = 0.8 * time_hours
    start_time15 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time15 < duration15:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 16
    duration16 = 1.2 * time_hours
    start_time16 = time()
    MFC1value = 20
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() - start_time16 < duration16:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

    # LOOP 17 (runs indefinitely)
    start_time17 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() > start_time17:
        # CSV logging
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2value = MFC2.mfc_read()

        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            timestr = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestr, MFC1value, MFC2value])

        update_mfc_data()
        sleep(5)
        update_mfc_data()
        sleep(5)

except KeyboardInterrupt:
    # On interruption, ensure any pending data is sent
    if mfc_data["MFC1"] or mfc_data["MFC2"] or mfc_data["timestamp"]:
        send_accumulated_data_to_database()
    pass
