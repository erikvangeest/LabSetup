import serial
from time import sleep, strftime, localtime, time
import csv
import sys
import os
from datetime import datetime

time_hours = 1800
additional_stabilization = 0 * time_hours #int(sys.argv[1]) * time_hours 

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

MFC1 = MassFlowController("COM18")

# Define the root folder path
root_folder = r'c:\Users\User\Documents\Git Repository\MFC logs'

# Create a new folder with the current date as its name
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = os.path.join(root_folder, current_date)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a CSV file with a timestamped name and write headers
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
csv_filename = os.path.join(folder_path, f"{timestamp}_MFC1 log_.csv")

with open(csv_filename, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Timestamp", "MFC1 Value"])

# Set the duration for the first loop (in hours)

duration1 = 1 * time_hours + additional_stabilization        
start_time1 = time()

MFCvalue = 180
MFC1.setValue(MFCvalue)
print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

try:
    while time() - start_time1 < duration1:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    # Set the duration for the second loop (200 seconds)
    duration2 = 1 * time_hours
    start_time2 = time()
    
    MFCvalue = 140
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

    while time() - start_time2 < duration2:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    # Set the duration for the second loop (200 seconds)
    duration3 = 1 * time_hours
    start_time3 = time()
    
    MFCvalue = 140
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

    while time() - start_time3 < duration3:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    start_time4 = time()

    MFCvalue = 140
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() > start_time4:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

except KeyboardInterrupt:
    pass