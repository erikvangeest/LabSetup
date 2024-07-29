import serial
from time import sleep, strftime, localtime, time
import csv
import sys
import os
from datetime import datetime

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

duration1 = 6 * time_hours + additional_stabilization     
start_time1 = time()

MFCvalue = 255
MFC1.setValue(MFCvalue)
print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

try:
    while time() - start_time1 < duration1:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    duration2 = 8 * time_hours
    start_time2 = time()

    MFCvalue = 193
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time2 < duration2:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    duration3 = 8 * time_hours
    start_time3 = time()

    MFCvalue = 175
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time3 < duration3:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)

    # 24:00 next day

    duration4 = 9 * time_hours
    start_time4 = time()

    MFCvalue = 255
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time4 < duration4:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)        

    duration5 = 7 * time_hours
    start_time5 = time()

    MFCvalue = 193
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time5 < duration5:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])

            sleep(10)

    duration6 = 7 * time_hours
    start_time6 = time()

    MFCvalue = 175
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time6 < duration6:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])

            sleep(10)        

    duration7 = 4 * time_hours
    start_time7 = time()

    MFCvalue = 0
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
    
    while time() - start_time7 < duration7:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])

            sleep(10)      

    duration8 = 7 * time_hours

    # Calculate the increment value per second to reach 255 in 12 hours
    increment_per_second = 255 / duration8
    start_time8 = time()
 
    MFCvalue = 0
    while True:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
    
        # Exit loop if 12 hours have passed
        if elapsed_time >= duration8:
            break
    
        # Calculate the new value based on elapsed time
        new_value = int(elapsed_time * increment_per_second)
        
        # Ensure the value does not exceed 255
        if new_value > 255:
            new_value = 255
        
        # Update MFCvalue    
        MFCvalue = new_value
        MFC1.setValue(MFCvalue)
        print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')
        
        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
        
        # Sleep for 10 seconds
        sleep(10)        

    
    start_time9 = time()
    MFCvalue = 0
    MFC1.setValue(MFCvalue)
    print(f'Timestamp: {timestamp}, MFC1 Value: {MFCvalue}')

    while time() > start_time9:

        with open(csv_filename, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime())
            csv_writer.writerow([timestamp, MFCvalue])
            
        sleep(10)      


except KeyboardInterrupt:
    pass