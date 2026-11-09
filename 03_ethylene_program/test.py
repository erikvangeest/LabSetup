

import serial
from time import sleep, strftime, localtime, time
import csv
import os
import sys
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_hours = 30 # change back to 3600   
additional_stabilization = time_hours * 1 #int(sys.argv[1])

# Timeout for read operations, in seconds
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
        sleep(0.1)
        if self.ser.in_waiting > 0:
            self.response = self.ser.read_until(b'>')
            self.response = self.response.decode('utf-8')  # Convert byte string to regular string
            self.response = self.response.replace('\r', '')  # Remove '\r'

    
            


MFC1 = MassFlowController(ser, adress = 12)
MFC2 = MassFlowController(ser, adress = 11)



# MFC2.mfc_mode(3)
MFC2.setValue(50)
MFC2.mfc_mode(1)

# MFC1.mfc_mode(3)
MFC1.setValue(100)
MFC1.mfc_mode(1)

ser.flush()

i = 0
while i < 10:
    print(f"MFC1: {MFC1.mfc_read()}")
    sleep(0.5)
    MFC2.mfc_read()
    print(f"MFC2: {MFC2.mfc_read()}")
    i += 1
    sleep(0.5)

# MFC1.mfc_read()
sleep(1)
MFC1.mfc_mode(3)
MFC2.mfc_mode(3)