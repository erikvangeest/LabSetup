import serial
from time import sleep, strftime, localtime, time
import csv
import os
from datetime import datetime

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

time_hours = 3600

MFC1 = MassFlowController("COM18")

# Define the root folder path
root_folder = r'c:\Users\User\Documents\Git Repository\environmental data logs'

# Create a new folder with the current date as its name
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = os.path.join(root_folder, current_date)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a CSV file with a timestamped name and write headers
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
csv_filename = os.path.join(folder_path, f"{timestamp}_MFC2 log_.csv")

with open(csv_filename, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Timestamp", "MFC2 Value"])

MFCvalue = 140
MFC1.setValue(MFCvalue)

try:
    while True:
        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            print(f'Timestamp: {timestamp}, MFC2 Value: {MFCvalue}')
        sleep(10)

except KeyboardInterrupt:
    pass