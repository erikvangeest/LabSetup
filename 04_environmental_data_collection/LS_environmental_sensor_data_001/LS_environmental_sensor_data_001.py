import os
import serial
import csv
import threading
from datetime import datetime
import time
from pathlib import Path

excel_file = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\LOG experimental settings.xlsx' 

# Check if the file exists
if os.path.isfile(excel_file):
    # Open the file with the default application
    os.startfile(excel_file)
else:
    print(f"File '{excel_file}' not found.")


# Define the serial ports and baud rate (adjust as needed)
ser1 = serial.Serial('COM22', 9600)     # Heater
ser2 = serial.Serial('COM15', 115200)   # SHT 20
ser3 = serial.Serial('COM20', 9600)     # MFC 2 solenoid (klep)
ser4 = serial.Serial('COM21', 9600)     # BME680


# Define the root folder path
root_folder = r'c:\Users\User\Documents\Git Repository\environmental data logs'

# Create a new folder with the current date as its name
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = os.path.join(root_folder, current_date)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a CSV file with a timestamped name and write headers
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
csv_filename = os.path.join(folder_path, f"{timestamp}_environmental_data_.csv")

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp1", "Heater1", "Heater2", "Heater3", "Heater4", "Timestamp2", "SHT20 Temperature", "SHT20 Humidity", "Timestamp3", "BME Temp", "BME Pressure", "BME Humidity", "BME tVOC", "Timestamp4", "Klep status"])

# Function to read data from a serial port and write to CSV
def read_and_log_data(serial_port, data_storage):
    while True:
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Read data from the serial port
        data = serial_port.readline().decode('utf-8').strip()

        # Split the data into values (assuming they are comma-separated)
        values = data.split(',')

        # Combine all data into a single list
        combined_data = [timestamp] + values

        # Store the combined data in the provided data_storage list
        data_storage[0] = combined_data

# Create threads for reading data from each serial port
ser1_data = [None]
ser2_data = [None]
ser3_data = [None]
ser4_data = [None]

ser1_thread = threading.Thread(target=read_and_log_data, args=(ser1, ser1_data))
ser2_thread = threading.Thread(target=read_and_log_data, args=(ser2, ser2_data))
ser3_thread = threading.Thread(target=read_and_log_data, args=(ser3, ser3_data))
ser4_thread = threading.Thread(target=read_and_log_data, args=(ser4, ser4_data))

# Start the threads
ser1_thread.start()
ser2_thread.start()
ser3_thread.start()
ser4_thread.start()

# Function to write the latest data from all COM ports to the CSV file every 5 seconds
def write_latest_data_to_csv(interval):
    while True:
        # Wait for 5 seconds
        time.sleep(interval)

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Combine the latest data from all COM ports with the current timestamp and setting value
        combined_data =  ser1_data[0] + ser2_data[0] + ser4_data[0] + ser3_data[0]

        # Append the combined data to the CSV file
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(combined_data)

        # Print the combined data to the console (optional)
        print("Writing to CSV:", combined_data)

# Set the interval for writing data (every 5 seconds)
write_interval = 5

# Start writing the latest data to the CSV file periodically
write_data_thread = threading.Thread(target=write_latest_data_to_csv, args=(write_interval,))
write_data_thread.start()