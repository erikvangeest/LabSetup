import serial
import schedule
from time import sleep
from datetime import datetime, timedelta
import json
import random
import os
import sys
import csv
import threading
import subprocess
import traceback

from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient

# --- Configuration ---
time_hours = 3600  # 1 hour in seconds
reset_interval = timedelta(hours=24)  # Reset every 24 hours
additional_stabilization = time_hours * int(sys.argv[1]) if len(sys.argv) > 1 else 0

# --- Experiment Configuration ---
EBOX_UID = "MFC_LABSETUP"
EBOX_SOFTWARE = "BURGERKING & WIJSVINGER INC. SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"
experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(open(r'C:\Users\User\Documents\Git Repository\Master codes\experiment_config.json'))

database = MQTTClient(EBOX_UID)
logger = None
frame_buffer = FrameBuffer(EBOX_UID, EBOX_SOFTWARE, SENSORHEAD_FIRMWARE, experiment_uid, list(experiment_config["receptors"].values()), logger)

print('Eth MFC script started')

# --- Global references ---
experiment_thread = None
stop_experiment = threading.Event()

# --- Mass Flow Controller Class ---
class MassFlowController:
    def __init__(self, port, address):
        self.ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        self.address = address
        self.response = ""

    def setValue(self, set_point):
        if self.ser.is_open:
            self.ser.write(f"*{self.address} V 4 ={set_point}\r\n".encode())
        self.read_data()

    def mfc_read(self):
        if self.ser.is_open:
            self.ser.write(f"*{self.address} F\r\n".encode())
        self.read_data()
        return self.response.strip(' SCCM>')

    def read_data(self):
        sleep(0.1)
        if self.ser.in_waiting > 0:
            self.response = self.ser.readline().decode('utf-8').replace('\r', '')

    def close(self):
        """Close the serial port to free COM20"""
        if self.ser and self.ser.is_open:
            print(f"🔴 Closing {self.ser.port}...")
            self.ser.close()
            self.ser = None

MFC1 = MassFlowController(port="COM13", address=11)
MFC2 = MassFlowController(port="COM14", address=12)

# --- Logging ---
root_folder = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\MFC logs'

def create_new_folder_for_current_date():
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(root_folder, current_date)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def create_new_csv_file(folder_path):
    tstamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    csv_filename = os.path.join(folder_path, f"{tstamp}_MFC1+MFC2_log.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "MFC1 Value", "MFC2 Value"])
    return csv_filename

def log_data_to_csv(csv_filename, MFC1value, MFC2value):
    with open(csv_filename, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), MFC1value, MFC2value])

# --- Main Experiment Function ---
def run_experiment():
    global stop_experiment
    stop_experiment.clear()  # Reset stop flag

    try:
        start_time = datetime.now()
        print(f"Experiment started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        current_folder_path = create_new_folder_for_current_date()
        csv_filename = create_new_csv_file(current_folder_path)

        subcycles = [
            {"duration": 0.8 * time_hours, "MFC2_setpoint": 0},
            {"duration": 1.2 * time_hours, "MFC2_setpoint": 2.5},
            {"duration": 0.8 * time_hours, "MFC2_setpoint": 0},
            {"duration": 1.2 * time_hours, "MFC2_setpoint": 5},
            {"duration": 0.8 * time_hours, "MFC2_setpoint": 0},
            {"duration": 1.2 * time_hours, "MFC2_setpoint": 10},
            {"duration": 0.8 * time_hours, "MFC2_setpoint": 0},
            {"duration": 1.2 * time_hours, "MFC2_setpoint": 20},
            {"duration": 0.8 * time_hours, "MFC2_setpoint": 0},
        ]
        
        MFC1.setValue(100)

        for cycle in subcycles:
            if stop_experiment.is_set():
                print("Experiment stopped.")
                return

            cycle_start_time = datetime.now()
            MFC2.setValue(cycle["MFC2_setpoint"])

            while (datetime.now() - cycle_start_time).total_seconds() < cycle["duration"]:
                if stop_experiment.is_set():
                    print("Experiment stopped.")
                    return

                MFC1value = MFC1.mfc_read()
                MFC2value = MFC2.mfc_read()
                print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, MFC1: {MFC1value}, MFC2: {MFC2value}')
                log_data_to_csv(csv_filename, MFC1value, MFC2value)
                sleep(5)

    except Exception as e:
        print("❌ Experiment crashed! Error:", str(e))
        traceback.print_exc()

# --- Stop Experiment Function ---
def stop_running_experiment():
    global stop_experiment, experiment_thread, MFC1, MFC2

    if experiment_thread and experiment_thread.is_alive():
        print("Stopping previous experiment...")
        stop_experiment.set()
        experiment_thread.join()

    # 🔴 Forcefully Close Serial Ports (COM20)
    try:
        if MFC1:
            MFC1.close()
            MFC1 = None  # Free memory reference
        if MFC2:
            MFC2.close()
            MFC2 = None  # Free memory reference
        print("✅ Serial ports closed.")
    except Exception as e:
        print(f"⚠️ Error closing serial ports: {e}")

    # 🔴 Kill All Threads That Might Be Using COM20
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            print(f"🔴 Stopping thread: {thread.name}")
            try:
                thread.join(timeout=1)
            except Exception as e:
                print(f"⚠️ Failed to stop thread {thread.name}: {e}")

    time.sleep(1)  # Allow time for the port to release


import serial.tools.list_ports

def is_port_in_use(port_name):
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return port_name in ports

import psutil
import serial.tools.list_ports
import time
import subprocess

def force_close_serial_port(port_name):
    """Attempts to close a serial port by finding and killing the process using it."""
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            if proc.info["cmdline"]:
                for arg in proc.info["cmdline"]:
                    if port_name in arg:
                        print(f"⚠️ Killing process {proc.info['name']} (PID: {proc.info['pid']}) using {port_name}...")
                        proc.terminate()  # Try to close it gracefully
                        time.sleep(1)
                        proc.kill()  # Force kill if still running
                        print(f"✅ {port_name} should now be free.")
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"⚠️ No process found using {port_name}.")
    return False

def flash_arduino(comport, arduino_path):
    """Ensure COM20 is closed before flashing the Arduino."""
    
    print(f"Flashing Arduino on {comport}...")
    subprocess.run(['arduino-cli.exe', 'compile', '--fqbn', 'arduino:avr:uno', arduino_path])
    subprocess.run(['arduino-cli.exe', 'upload', '-p', comport, '--fqbn', 'arduino:avr:uno', arduino_path])

    # Ensure COM20 is properly closed after flashing
    try:
        ser = serial.Serial(comport, 9600)
        ser.close()
        print(f"✅ Successfully closed {comport} after flashing.")
    except Exception as e:
        print(f"⚠️ Error closing {comport} after flashing: {e}")

        
ETHYLENE_ARDUINO_PATH = f'./03_ethylene_program/ethylene_program_016//LS_valve_ethylene_program_016/LS_valve_ethylene_program_016.ino'
ETHYLENE_ARDUINO_PORT = 'COM20'

# --- Scheduled Function ---
def safe_schedule_check():
    global experiment_thread
    print(f"Schedule check @ {datetime.now().strftime('%H:%M')}")
    now = datetime.now().strftime("%H:%M")
    if now == "15:15":
        print("Starting new experiment...")
        stop_running_experiment()

        # Flash Arduino
        flash_arduino(ETHYLENE_ARDUINO_PORT, ETHYLENE_ARDUINO_PATH)

        # Start new experiment
        experiment_thread = threading.Thread(target=run_experiment, daemon=True)
        experiment_thread.start()

# --- Start the Scheduler ---
schedule.every(30).seconds.do(safe_schedule_check)

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
            sleep(10)
        except Exception as e:
            print("Scheduler error:", str(e))
            traceback.print_exc()

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Keep the main script alive indefinitely
while True:
    try:
        sleep(10)
    except KeyboardInterrupt:
        print("Stopping script...")
        stop_running_experiment()
        break