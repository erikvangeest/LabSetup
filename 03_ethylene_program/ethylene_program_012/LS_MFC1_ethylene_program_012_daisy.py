import serial
from time import sleep, strftime, localtime, time
import csv
import os
import sys
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 30 # change back to 3600   
additional_stabilization = time_hours * 1 #int(sys.argv[1])

ser = serial.Serial(
port= "COM13",    # Replace with your port (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux)
baudrate=9600,          # Common baud rate, can adjust based on your device's requirements
timeout=1)     

class MassFlowController:
    def __init__(self, ser, adress):
        self.ser = ser
        self.adress = adress

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
        sleep(0.2)
        if self.ser.in_waiting > 0:
            self.response = self.ser.readline()
            self.response = self.response.decode('utf-8')  # Convert byte string to regular string
            self.response = self.response.replace('\r', '')  # Remove '\r'
    
            


MFC1 = MassFlowController(ser, adress = 12)
MFC2 = MassFlowController(ser, adress = 11)

# MFC1.mfc_mode(3)
# MFC1.set_point(100)
# MFC1.mfc_mode(1)

# i = 0
# while i < 10:
#     MFC1.mfc_read()
#     i += 1
#     sleep(1)

# MFC1.mfc_read()
# # mfc1.read_data()
# sleep(1)
# MFC1.mfc_mode(3)

#=======================================================================================================

#Define the root folder path

#root_folder = r'c:\Users\User\Documents\Git Repository\MFC logs'
root_folder = r'c:\Users\User\OneDrive - SmartSense BV\2 Product Team\Product Development Team\Wafer dies\MFC logs'


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

duration1 = additional_stabilization     
start_time1 = time()

MFC1value = 0  
MFC2value = 50    # normal = 140

MFC1.setValue(MFC1value)
MFC2.setValue(MFC2value)
MFC1.mfc_mode(1)
MFC2.mfc_mode(1)
print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

try:
    while time() - start_time1 < duration1:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        MFC2.mfc_read()
        MFC2value = MFC2.mfc_read()

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])
            print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
        sleep(10)

    duration2 = 2 * time_hours
    start_time2 = time()

    MFC1value = 20
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time2 < duration2:

               
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        # MFC2value = MFC2.mfc_read()

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

    duration3 = 2 * time_hours
    start_time3 = time()

    MFC1value = 10
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time3 < duration3:
             
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        # MFC2value = MFC2.mfc_read()

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

    duration4 = 2 * time_hours
    start_time4 = time()

    MFC1value = 5
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time4 < duration4:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        # MFC2value = MFC2.mfc_read()

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

    duration5 = 2 * time_hours
    start_time5 = time()

    MFC1value = 3
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time5 < duration5:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        # MFC2value = MFC2.mfc_read()

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
  
    start_time6 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() > start_time6:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MFC1value = MFC1.mfc_read()
        # MFC2value = MFC2.mfc_read()

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


except KeyboardInterrupt:
    pass