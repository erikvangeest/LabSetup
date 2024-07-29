import serial
from time import sleep, strftime, localtime, time
import csv
import os
import sys
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 3600   
additional_stabilization = int(sys.argv[1]) * time_hours

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
    csv_filename = os.path.join(folder_path, f"{timestamp}_MFC1+MFC2_log.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "MFC1 Value", "MFC2 Value"])
    return csv_filename


# Function to check if a CSV file with "MFC" exists in the current folder
def check_csv_exists(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if 'MFC1+MFC2_log.csv' in f]
    return len(csv_files) > 0

# Get initial folder and CSV file
current_folder_path = create_new_folder_for_current_date()
if not check_csv_exists(current_folder_path):
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

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

        sleep(10)

    duration2 = 8 * time_hours
    start_time2 = time()

    MFC1value = 193
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time2 < duration2:

               
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

            
        sleep(10)

    duration3 = 8 * time_hours
    start_time3 = time()

    MFC1value = 175
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time3 < duration3:
             
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

            
        sleep(10)

    # 24:00 next day

    duration4 = 9 * time_hours
    start_time4 = time()

    MFC1value = 255
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time4 < duration4:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

        sleep(10)        

    duration5 = 7 * time_hours
    start_time5 = time()

    MFC1value = 193
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time5 < duration5:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

            sleep(10)

    duration6 = 7 * time_hours
    start_time6 = time()

    MFC1value = 175
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time6 < duration6:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

            sleep(10)        

    duration7 = 4 * time_hours
    start_time7 = time()

    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
    
    while time() - start_time7 < duration7:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])

            sleep(10)      

    duration8 = 7 * time_hours

    # Calculate the increment value per second to reach 255 in 12 hours
    increment_per_second = 255 / duration8
    start_time8 = time()
 
    MFC1value = 0
    while time() - start_time8 < duration8:
        # Calculate elapsed time
        elapsed_time = time() - start_time8
    
        # Exit loop if 12 hours have passed
        if elapsed_time >= duration8:
            break
    
        # Calculate the new value based on elapsed time
        new_value = int(elapsed_time * increment_per_second)
        
        # Ensure the value does not exceed 255
        if new_value > 255:
            new_value = 255
        
        # Update MFCvalue    
        MFC1value = new_value
        MFC1.setValue(MFC1value)
        print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])
        
        # Sleep for 10 seconds
        sleep(10)        

    
    start_time9 = time()
    MFC1value = 0
    MFC1.setValue(MFC1value)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFC1value}, MFC2 value: {MFC2value}')

    while time() > start_time9:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if date has changed and create new folder and CSV file accordingly
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(os.path.join(root_folder, current_date)):
            current_folder_path = create_new_folder_for_current_date()
            csv_filename = create_new_csv_file(current_folder_path)

        # Check if CSV file with "MFC" exists, if not, create one
        if not check_csv_exists(current_folder_path):
            csv_filename = create_new_csv_file(current_folder_path)            

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFC1value, MFC2value])
            
        sleep(10)      


except KeyboardInterrupt:
    pass