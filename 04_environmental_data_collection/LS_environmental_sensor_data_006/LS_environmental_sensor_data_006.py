import serial
import csv
import threading
from datetime import datetime, date
import time

import numpy as np
from time import sleep
from matplotlib import pyplot as plt
from datetime import datetime
import os
from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient
import random
import json

EBOX_UID = "VALVE_LABSETUP"
EBOX_SOFTWARE = "NIGEL INC SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"
experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(open(r'C:\Users\User\Documents\Git Repository\Master codes\experiment_config.json'))

database = MQTTClient(EBOX_UID)
import atexit
database.connect()

atexit.register(database.disconnect)

logger = None

frame_buffer = FrameBuffer(EBOX_UID, EBOX_SOFTWARE, SENSORHEAD_FIRMWARE, experiment_uid, list(experiment_config["receptors"].values()), logger)

excel_file = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\LOG experimental settings.xlsx'

# Check if the file exists
if os.path.isfile(excel_file):
    # Open the file with the default application
    os.startfile(excel_file)
else:
    print(f"File '{excel_file}' not found.")

# Define the serial ports and baud rate (adjust as needed)
#ser1 = serial.Serial('COM22', 9600)     # Heater
#ser2 = serial.Serial('COM15', 115200)   # SHT 20
#ser3 = serial.Serial('COM20', 9600)     # MFC 2 solenoid (klep)
#ser4 = serial.Serial('COM17', 9600)     # BME680

# Define the root folder path

#root_folder = r'c:\Users\User\Documents\Git Repository\environmental data logs'
root_folder = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\Environmental logs'

# Function to create a new folder for the current date
def create_new_folder_for_current_date():
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(root_folder, current_date)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

# Function to create a new CSV file with timestamped name and headers
def create_new_csv_file(folder_path):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    csv_filename = os.path.join(folder_path, f"{timestamp}_environmental_data_.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp1", "Klep status"])
    return csv_filename

# Get initial folder and CSV file
current_folder_path = create_new_folder_for_current_date()
csv_filename = create_new_csv_file(current_folder_path)

# Function to read data from a serial port and write to CSV
def read_and_log_data(serial_port, data_storage):
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = serial_port.readline().decode('utf-8').strip()
        # print(data)
        values = data.split(',')
        combined_data = [timestamp] + values
        data_storage[0] = combined_data

# Create threads for reading data from each serial port
#ser1_data = [None]
#ser2_data = [None]
ser3_data = [None]
#ser4_data = [None]

#ser1_thread = threading.Thread(target=read_and_log_data, args=(ser1, ser1_data))
#ser2_thread = threading.Thread(target=read_and_log_data, args=(ser2, ser2_data))
ser3_thread = threading.Thread(target=read_and_log_data, args=(ser3, ser3_data))
#ser4_thread = threading.Thread(target=read_and_log_data, args=(ser4, ser4_data))

# Start the threads
#ser1_thread.start()
#ser2_thread.start()
ser3_thread.start()
#ser4_thread.start()


# Initialize accumulators for each sensor
accumulated_data = {
    "valve_1": [],
    "timestamp": [],
}

# Function to append new data to accumulators
# Function to append new data to accumulators
def append_to_accumulators():
    try:
        if ser3_data and ser3_data[0]:
            # Safely parse valve status
            valve_status = (
                float(ser3_data[0][1])
                if len(ser3_data[0]) > 1 and ser3_data[0][1].replace('.', '', 1).isdigit()
                else None
            )
            accumulated_data["valve_1"].append(valve_status)
            timestamp = datetime.now().timestamp()
            accumulated_data["timestamp"].append(timestamp)
            #print('Accumulated data:', accumulated_data)
        else:
            print("No valid data found in 'ser3_data' to append.")
    except KeyError as e:
        print(f"Key error while appending to accumulators: {e}")
    except ValueError as e:
        print(f"Value error while parsing valve status: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while appending to accumulators: {e}")

# Function to send accumulated data to the database
def send_accumulated_data_to_database():
    #print("Sending accumulated data to the database...")
    global accumulated_data
    try:
        frame_buffer.generate_environmental_frame(
            sensorhead_name="SensorheadLS",  # Update with the correct name
            start_time=datetime.now().timestamp(),
            measurement_data=accumulated_data
        )
        #print('Measurement data:', accumulated_data)
        
        if frame_buffer.get_size() > 0:
            try:
                # database.connect()
                print('Database connected')
                
                for frame in frame_buffer.get_frames():
                    try:
                        database.upload(frame.model_dump_json())
                        sleep(0.1)  # Throttle upload to avoid overloading the server
                    except Exception as e:
                        print(f"Failed to upload a frame: {e}")
                        
                frame_buffer.clear_frames()
                print("Uploaded valve data to the database successfully.")
            except Exception as e:
                print(f"Database operation error: {e}")
            finally:
                try:
                    # database.disconnect()
                    print("Database disconnected.")
                except Exception as e:
                    print(f"Failed to disconnect from the database: {e}")
        else:
            print("No frames in the frame buffer to upload.")
    except KeyError as e:
        print(f"Key error while generating environmental frame: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while sending data to the database: {e}")
    finally:
        # Ensure accumulated data is cleared
        try:
            for key in accumulated_data:
                accumulated_data[key].clear()
            print("Cleared accumulated data.")
        except Exception as e:
            print(f"Failed to clear accumulated data: {e}")
            
# Function to write the latest data to the CSV file every 5 seconds
def write_latest_data_to_csv(interval, send_interval):
    global csv_filename  # Declare csv_filename as global to access and modify it within the function
    start_date = datetime.now().date()
    last_send_time = time.time()

    while True:
        time.sleep(interval)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().date()
        if current_date != start_date:
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)
            start_date = current_date

        # Append data to accumulators
        append_to_accumulators()
        #print('ser4data', ser4_data)
        print('ser3data', ser3_data)
        # print('ser2data', ser2_data)
        # print('ser1data', ser1_data)
        # Write data to CSV
        combined_data = ser3_data[0] #+ ser4_data[0]      #ser1_data[0] + ser2_data[0]  + ser3_data[0]
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(combined_data)
        #print("Writing to CSV:", combined_data)

        # Send data to the database every send_interval seconds
        if time.time() - last_send_time >= send_interval:
            send_accumulated_data_to_database()
            last_send_time = time.time()

# Set the interval for writing data (every 5 seconds) and sending data (every 2 minutes)
write_interval = 5
send_interval = 120

# Start writing the latest data to the CSV file periodically
write_data_thread = threading.Thread(target=write_latest_data_to_csv, args=(write_interval, send_interval))
write_data_thread.start()

