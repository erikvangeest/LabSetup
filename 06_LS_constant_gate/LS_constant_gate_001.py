
import pyvisa as visa
import time 
import csv
import os
from datetime import datetime
from time import sleep
import subprocess

from keithley import DMM6500
from rigol import DP2031
from flogger import Flogger, generateTimestampString
import numpy as np

HEATING_PROGRAM = 'cure'		# Program 008 and higher are for heating on chip with receptor V2
ETHYLENE_PROGRAM = '013'		# Ethylene program 009 and higher is for bypass valve & double MFC logging. 
ENVIRONMENTAL_PROGRAM = '002'
additional_stabilization =  0 #hours

gate_voltage = 0 # gate voltage set


# log title - experiment information
chip_identifier1 = 	"ID_097" 	# fill in chip number positioned in slot 1
chip_identifier2 = 	"ID_098" 	# fill in chip number positioned in slot 2 
chip_identifier3 = 	"ID_099" 	# fill in chip number positioned in slot 3
chip_identifier4 = 	"ID_100" 	# fill in chip number positioned in slot 4

chip_identifier5 = 	"ID_" 	# fill in chip number positioned in slot 5
chip_identifier6 = 	"ID_" 	# fill in chip number positioned in slot 6
chip_identifier7 = 	"ID_" 	# fill in chip number positioned in slot 7

conditions1 = 		"blot, solder ball, bis ethx adip cu KroCo3 1% TBA, flip die, individual" 		# fill in conditions 1		do not use - sign in the conditions!
conditions2 = 		"blot, solder ball, bis ethx adip cu KroCo3 1% TBA, flip die, individual" 		# fill in conditions 2
conditions3 = 		"blot, solder ball, bis ethx adip ligand KroCo3 1% TBA, flip die, individual" 		# fill in conditions 3
conditions4 = 		"blot, solder ball, bis ethx adip ligand KroCo3 1% TBA, flip die, individual" 		# fill in conditions 4

conditions5 = 		"" 		# fill in conditions 5
conditions6 = 		"" 		# fill in conditions 6
conditions7 = 		"" 		# fill in conditions 7


ETHYLENE_PROGRAM_PATH = rf'c:\Users\User\Documents\Git Repository\Master codes\03_ethylene_program\ethylene_program_{ETHYLENE_PROGRAM}\LS_MFC1_ethylene_program_{ETHYLENE_PROGRAM}.py'

ETHYLENE_ARDUINO_PATH = rf'c:\Users\User\Documents\Git Repository\Master codes\03_ethylene_program\ethylene_program_{ETHYLENE_PROGRAM}\LS_valve_ethylene_program_{ETHYLENE_PROGRAM}\LS_valve_ethylene_program_{ETHYLENE_PROGRAM}.ino'
ETHYLENE_ARDUINO_PORT = 'COM20'

HEATER_ARDUINO_PORT = 'COM22'
HEATER_ARDUINO_PATH = rf'c:\Users\User\Documents\Git Repository\Master codes\01_heating_program\LS_heating_program_{HEATING_PROGRAM}\LS_heating_program_{HEATING_PROGRAM}.ino'

ENVIRONMENTAL_PROGRAM_PATH = rf'c:\Users\User\Documents\Git Repository\Master codes\04_environmental_data_collection\LS_environmental_sensor_data_{ENVIRONMENTAL_PROGRAM}\LS_environmental_sensor_data_{ENVIRONMENTAL_PROGRAM}.py'


PSU_address = "TCPIP0::192.168.10.61::inst0::INSTR"
PSU = DP2031(PSU_address)
v_gate_channel = PSU.channel1

# configure output channels 1 and 2 in series
PSU.set_channel_pairing('SER')
sleep(3)
v_gate_channel.set_output(1)
v_gate_channel.set_voltage_current(gate_voltage/2, 0.1)
sleep(3)


def createFlogger(logDirBase, logName, datedFolders=False):
	if(datedFolders == True):
		dirTimestamp = datetime.now().strftime("%Y-%m-%d")
		logDir = logDirBase + "_" + dirTimestamp
		if not os.path.exists(logDir):
			os.makedirs(logDir)
	else:
		logDir = logDirBase

	if not os.path.exists(logDir):
			os.makedirs(logDir)

	fileTimeStamp = generateTimestampString()
	logFile = logDir + "/" + fileTimeStamp + "_" + logName + ".csv"
	newFlogger = Flogger(logFile, ",")
	newFlogger.createFile()
	newFlogger.logRow(["timestamp", "channel", "cycle_number", "Elapsed time (hours)", "Resistance (Ohm)"])
	# edit these to format data in log
	newFlogger.setFormatStrings(["{}", "{}", "{}", "{}", "{:.6f}"])
	return newFlogger


def cycleChannels():
	global nChannels, currentChannelIndex
	currentChannelIndex = ((currentChannelIndex + 1) % nChannels)
	#print(f"current channel: {currentChannelIndex + 1}")
	return sampleChannels[currentChannelIndex]

def flash_arduino(comport, arduino_path):
	subprocess.run(['arduino-cli.exe', 'compile', '--fqbn', 'arduino:avr:uno', arduino_path])
	subprocess.run(['arduino-cli.exe', 'upload', '-p', comport, '--fqbn', 'arduino:avr:uno', arduino_path])


class Multimeter:


	def __init__(self, usbAddress):
		self.device = DMM6500(visa.ResourceManager().open_resource(usbAddress))


	def reset(self):
		self.device.reset()


	def measureResistance(self):
		self.device.function = Function.RESISTANCE
		sampleValue = self.device.measure()
		return sampleValue


class Switch:


	def __init__(self, gpibAddress):
		self.gpibAdapter = gpibAdapter = visa.ResourceManager().open_resource(gpibAddress)
		self.gpibAdapter.timeout = 10000


	def disconnectChannel(self, slot, channel):
		self.gpibAdapter.write(f"ROUT:OPEN (@{slot:02d}!{channel:02d})")


	def connectChannel(self, slot, channel):
		self.gpibAdapter.write(f"ROUT:CLOS (@{slot:02d}!{channel:02d})")

	def disconnectAllChannels(self, slot):
		commandString = "ROUT:OPEN ALL"
		self.gpibAdapter.write(commandString)


class MeasurementChannel:

	#switchDelay = 2e-3 # channel switch delay in seconds
	switchDelay = 0.002

	def __init__(self, Flogger, Multimeter, Switch, slot, channel):
		self.Flogger = Flogger
		self.Multimeter = Multimeter
		self.Switch = Switch
		self.slot = slot
		self.channel = channel
		self.startTime = datetime.now()
		self.cycle_number = 1  # Initialize the cycle number to 1

	def select(self):
		self.Switch.disconnectAllChannels(self.slot)
		self.Switch.connectChannel(self.slot, self.channel)
		time.sleep(self.switchDelay)


	def sampleChannelResistance(self, log=False):
		resistanceValue = float(self.Multimeter.measure('RES', 'defbuffer1', ['READ']))
		if(log == True):
			timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]
			elapsedTime = datetime.now() - self.startTime
			logData = [timestamp, self.channel, self.cycle_number, elapsedTime, resistanceValue]
			self.Flogger.logRow(logData)
		return resistanceValue
	
	def incrementCycle(self):
		self.cycle_number += 1
	# Add a method to increment the cycle number



gpibAddress = "GPIB0::7::INSTR"
usbAddress = "USB0::0x05E6::0x6500::04583480::INSTR"
PSU_address = 'TCPIP0::192.168.10.61::inst0::INSTR'
DMM_address = 'TCPIP0::192.168.10.71::inst0::INSTR'

with open(ETHYLENE_ARDUINO_PATH, 'r') as f:
	lines = f.readlines()

lines[0] = f'int additional_stabilization = {additional_stabilization};\n'

with open(ETHYLENE_ARDUINO_PATH, 'w') as f:
	f.writelines(lines)

flash_arduino(HEATER_ARDUINO_PORT, HEATER_ARDUINO_PATH)
flash_arduino(ETHYLENE_ARDUINO_PORT, ETHYLENE_ARDUINO_PATH)

# Start air program

subprocess.Popen(['python', ETHYLENE_PROGRAM_PATH, str(additional_stabilization)])
subprocess.Popen(['python', ENVIRONMENTAL_PROGRAM_PATH])

nChannels = 16
currentChannelIndex = 0

usedChannels = nChannels
Keithley7002 = Switch(gpibAddress)
Keithley6500 = DMM6500(DMM_address)
PSU = DP2031(PSU_address)

logDir = "./logs/"
logFileBase = "multimeter_log"
fileTimeStamp = generateTimestampString()
logFile = fileTimeStamp + logFileBase + ".csv" 
DataLogger = Flogger(logFile, ",")
DataLogger.createFile()


logDir = "./logs"
channel1Flogger = createFlogger(logDir, "channel1", datedFolders=True)
channel2Flogger = createFlogger(logDir, "channel2", datedFolders=True)
channel3Flogger = createFlogger(logDir, "channel3", datedFolders=True)
channel4Flogger = createFlogger(logDir, "channel4", datedFolders=True)
channel5Flogger = createFlogger(logDir, "channel5", datedFolders=True)
channel6Flogger = createFlogger(logDir, "channel6", datedFolders=True)
channel7Flogger = createFlogger(logDir, "channel7", datedFolders=True)
channel8Flogger = createFlogger(logDir, "channel8", datedFolders=True)

channel9Flogger = createFlogger(logDir, "channel9", datedFolders=True)
channel10Flogger = createFlogger(logDir, "channel10", datedFolders=True)
channel11Flogger = createFlogger(logDir, "channel11", datedFolders=True)
channel12Flogger = createFlogger(logDir, "channel12", datedFolders=True)
channel13Flogger = createFlogger(logDir, "channel13", datedFolders=True)
channel14Flogger = createFlogger(logDir, "channel14", datedFolders=True)
channel15Flogger = createFlogger(logDir, "channel15", datedFolders=True)
channel16Flogger = createFlogger(logDir, "channel16", datedFolders=True)

# in this section you can add more channels
SampleChannel1 = MeasurementChannel(channel1Flogger, Keithley6500, Keithley7002, 10, 1)
SampleChannel2 = MeasurementChannel(channel2Flogger, Keithley6500, Keithley7002, 10, 2)
SampleChannel3 = MeasurementChannel(channel3Flogger, Keithley6500, Keithley7002, 10, 3)
SampleChannel4 = MeasurementChannel(channel4Flogger, Keithley6500, Keithley7002, 10, 4)
SampleChannel5 = MeasurementChannel(channel5Flogger, Keithley6500, Keithley7002, 10, 5)
SampleChannel6 = MeasurementChannel(channel6Flogger, Keithley6500, Keithley7002, 10, 6)
SampleChannel7 = MeasurementChannel(channel7Flogger, Keithley6500, Keithley7002, 10, 7)
SampleChannel8 = MeasurementChannel(channel8Flogger, Keithley6500, Keithley7002, 10, 8)

SampleChannel9 = MeasurementChannel(channel9Flogger, Keithley6500, Keithley7002, 10, 11)
SampleChannel10 = MeasurementChannel(channel10Flogger, Keithley6500, Keithley7002, 10, 12)
SampleChannel11 = MeasurementChannel(channel11Flogger, Keithley6500, Keithley7002, 10, 13)
SampleChannel12 = MeasurementChannel(channel12Flogger, Keithley6500, Keithley7002, 10, 14)
SampleChannel13 = MeasurementChannel(channel13Flogger, Keithley6500, Keithley7002, 10, 15)
SampleChannel14 = MeasurementChannel(channel14Flogger, Keithley6500, Keithley7002, 10, 16)
SampleChannel15 = MeasurementChannel(channel15Flogger, Keithley6500, Keithley7002, 10, 17)
SampleChannel16 = MeasurementChannel(channel16Flogger, Keithley6500, Keithley7002, 10, 18)

sampleChannels = []

'''sampleChannels.append(SampleChannel1)
sampleChannels.append(SampleChannel2)
sampleChannels.append(SampleChannel3)
sampleChannels.append(SampleChannel4)
sampleChannels.append(SampleChannel5)
sampleChannels.append(SampleChannel6)
sampleChannels.append(SampleChannel7)
sampleChannels.append(SampleChannel8)'''

sampleChannels.append(SampleChannel9)
sampleChannels.append(SampleChannel10)
sampleChannels.append(SampleChannel11)
sampleChannels.append(SampleChannel12)
sampleChannels.append(SampleChannel13)
sampleChannels.append(SampleChannel14)
sampleChannels.append(SampleChannel15)
sampleChannels.append(SampleChannel16)

channelSwitchInterval = 2 # seconds

currentChannel = sampleChannels[0]
currentChannel.select()

lastSwitchTime = time.time()

"""

Keithley7002.connectChannel(1)
Keithley7002.connectChannel(2)
Keithley7002.connectChannel(3)
Keithley7002.connectChannel(4)
Keithley7002.connectChannel(5)


while(1):
	pass
"""

while(1):
	if(time.time() - lastSwitchTime >= channelSwitchInterval):
		currentChannel = cycleChannels()
		currentChannel.select()
		lastSwitchTime = time.time()
		time.sleep(0.5)
		currentChannel.incrementCycle()
	
	currentChannel.sampleChannelResistance(log=True)
	#change sampling speed (sleep 0 = fastest)
	time.sleep(0.1)
