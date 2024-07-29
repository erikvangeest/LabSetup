import serial
from time import sleep, strftime, localtime, time
import csv
import os
from datetime import datetime

time_hours = 5
additional_stabilization = 6 * time_hours  # For testing
# additional_stabilization = int(sys.argv[1]) * time_hours

duration1 = 6 * time_hours + additional_stabilization


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

# Define the root folder path
root_folder = r'c:\Users\User\Documents\Git Repository\environmental data logs'


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
    csv_filename = os.path.join(folder_path, f"{timestamp}_MFC1_log.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "MFC1 Value"])
    return csv_filename


# Get initial folder and CSV file
current_folder_path = create_new_folder_for_current_date()
csv_filename = create_new_csv_file(current_folder_path)

start_time1 = time()

MFCvalue = 255
MFC1.setValue(MFCvalue)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

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
            csv_writer.writerow([timestamp, MFCvalue])

        sleep(10)

except KeyboardInterrupt:
    pass

