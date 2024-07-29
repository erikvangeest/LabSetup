import serial
from time import sleep, strftime, localtime, time
import csv
import os
import sys
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 3600
additional_stabilization = time_hours * int(sys.argv[1])


class MassFlowController:

    defaultbaud = 9600

    def __init__(self, port):
        self.comport = serial.Serial()
        self.comport.port = port
        self.comport.baudrate = self.defaultbaud

    def writeByte(self, byte):
        self.comport.open()
        sleep(5)
        temp = bytes([byte])
        print(temp)
        self.comport.write(temp)
        self.comport.close()

    def setValue(self, pwm):
        self.writeByte(pwm)


MFC1 = MassFlowController("COM17")
MFC2 = MassFlowController("COM18")

# Define the root folder path
root_folder = r'c:\Users\User\Documents\Git Repository\MFC logs'


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
    csv_filename = os.path.join(folder_path, f"{timestamp}_MFC1+MFC2_log.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "MFC1 Value", "MFC2 Value"])
    return csv_filename


# Get initial folder and CSV file
current_folder_path = create_new_folder_for_current_date()
csv_filename = create_new_csv_file(current_folder_path)

duration1 = 6 * time_hours + additional_stabilization     
start_time1 = time()

MFC1value = 255       
MFC2value = 140

MFC1.setValue(MFC1value)
MFC2.setValue(MFC2value)
print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

try:
    while time() - start_time1 < duration1:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])
        
            
        sleep(10)


    start_time2 = time()

    MFC1value = 0

    MFC1.setValue(MFC1value)

    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() > start_time2:

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

        sleep (10)

except KeyboardInterrupt:
    pass