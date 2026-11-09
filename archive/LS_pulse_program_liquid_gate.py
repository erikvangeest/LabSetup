import numpy as np
from time import sleep
from matplotlib import pyplot as plt
from datetime import datetime
import os
import subprocess
#from smartsense.sensorhead.modbus_client import ModbusClient
from smartsense.sensorhead.frame_buffer import FrameBuffer
from smartsense.cloud.clients import MQTTClient
import random
import json
import numpy as np
from time import sleep
from matplotlib import pyplot as plt
from datetime import datetime
import os
import subprocess
from keithley import DMM6500#
from keithley import Switch700X
from rigol import DP2031
from flogger import Flogger

EBOX_UID = "EBOX_LS_09122024"
EBOX_SOFTWARE = "NIGEL INC SOFTWARE"
SENSORHEAD_FIRMWARE = "SensorheadLS"
experiment_uid = "%032x" % random.getrandbits(128)
experiment_config = json.load(open(r'C:\Users\User\Documents\Git Repository\Master codes\experiment_config.json'))

database = MQTTClient(EBOX_UID)

HUMIDITY_PROGRAM = '003'			# for stable humidity use "HIGH" for high humidity or "LOW" for low humidity.	
ETHYLENE_PROGRAM = '017'			# Ethylene program 009 and higher is for bypass valve & double MFC logging. Standard is 014
ENVIRONMENTAL_PROGRAM = '004'		# Environmental program 003 and higher is for logging of environmental data using Sensorhead-LS hybrid
additional_stabilization = 0 #hours

logger = None
frame_buffer = FrameBuffer(EBOX_UID, EBOX_SOFTWARE, SENSORHEAD_FIRMWARE, experiment_uid, list(experiment_config["receptors"].values()), logger)
# modbus_client = ModbusClient("/dev/ttyAMA0", 2000000)


# log title - experiment information
chip_identifier1 =  000 	# fill in chip number positioned in slot 1
chip_identifier2 = 	000 	# fill in chip number positioned in slot 2 
chip_identifier3 = 	5552 	# fill in chip number positioned in slot 3
chip_identifier4 = 	000 	# fill in chip number positioned in slot 4

chip_identifier5 = 	"ID_" 	# fill in chip number positioned in slot 5
chip_identifier6 = 	"ID_" 	# fill in chip number positioned in slot 6
chip_identifier7 = 	"ID_" 	# fill in chip number positioned in slot 7

conditions1 = 		"" 		# fill in conditions 1		do not use - sign in the conditions!
conditions2 = 		"" 		# fill in conditions 2
conditions3 = 		"PVD die 5 - act anisole" 		# fill in conditions 3
conditions4 = 		"SH" 		# fill in conditions 4
 
conditions5 = 		"" 		# fill in conditions 5
conditions6 = 		"" 		# fill in conditions 6
conditions7 = 		"" 		# fill in conditions 7

sweep_counter = 0
sweep_buffer = {"voltage": [], "resistance": []}


ETHYLENE_PROGRAM_PATH = f'./03_ethylene_program/ethylene_program_{ETHYLENE_PROGRAM}/LS_MFC1_ethylene_program_{ETHYLENE_PROGRAM}.py'

ETHYLENE_ARDUINO_PATH = f'./03_ethylene_program/ethylene_program_{ETHYLENE_PROGRAM}//LS_valve_ethylene_program_{ETHYLENE_PROGRAM}/LS_valve_ethylene_program_{ETHYLENE_PROGRAM}.ino'
ETHYLENE_ARDUINO_PORT = 'COM20'

HUMIDITY_ARDUINO_PORT = 'COM15'
HUMIDITY_ARDUINO_PATH = f'./07_humidity_program\LS_humidity_program_{HUMIDITY_PROGRAM}/LS_humidity_program_{HUMIDITY_PROGRAM}.ino'

ENVIRONMENTAL_PROGRAM_PATH = f'./04_environmental_data_collection/LS_environmental_sensor_data_{ENVIRONMENTAL_PROGRAM}/LS_environmental_sensor_data_{ENVIRONMENTAL_PROGRAM}.py'

def perform_voltage_sweep(DMM, PSUChannel, v_vector, delay):
	# create buffer for SD potential measurements
	r_dmm = np.zeros((len(v_vector)))

	# configure remote buffer on DMM
	buffer_name = 'voltageSweep0'
	buffer_size = 10
	DMM.create_buffer(buffer_name, buffer_size, 'STAN')
	DMM.set_buffer_mode(buffer_name, 'CONT')
	DMM.set_measure_count(1)

	# set PSU output and DMM measure mode
	PSUChannel.set_voltage_current(v_vector[0]/2, 0.1)
	DMM.measure('RES', buffer_name, ['READ'])
	
	# wait for PSU output to settle
	sleep(0.5)

	# perform voltage sweep, taking measurements after every PSU update
	for i,v in enumerate(v_vector):
		PSUChannel.set_voltage_current(v/2, 0.1)
		sleep(delay)
		r_dmm[i] = DMM.measure('RES', buffer_name, ['READ'])

	DMM.delete_buffer(buffer_name)

	return r_dmm


def perform_symmetric_voltage_sweep(DMM, PSUChannel, v_vector, delay):
	r_dmm_up = perform_voltage_sweep(DMM, PSUChannel, v_vector, delay)
	r_dmm_down = perform_voltage_sweep(DMM, PSUChannel, v_vector[::-1], delay)
	return [r_dmm_up, r_dmm_down[::-1]]

		
def flash_arduino(comport, arduino_path):
	subprocess.run(['arduino-cli.exe', 'compile', '--fqbn', 'arduino:avr:uno', arduino_path])
	subprocess.run(['arduino-cli.exe', 'upload', '-p', comport, '--fqbn', 'arduino:avr:uno', arduino_path])

class GateSweepChannel:


	switch_delay = 0.5 # was 2e-3, set higher to prevent 1st data point O.L.


	def __init__(self, DMM, PSUChannel, Switch, slot, channel_number, identifier, comment):
		self.DMM = DMM
		self.PSUChannel = PSUChannel
		self.Switch = Switch
		self.slot = slot
		self.channel_number = channel_number
		self.identifier = identifier
		self.comment = comment
		self.cycle_number = 0


	def set_sweep_parameters(self, v_vector, delay):
		self.v_vector = v_vector
		self.delay = delay


	def set_log_directory(self, log_dir):
		self.log_dir = log_dir


	def select(self):
		self.Switch.disconnect_all(self.slot)
		self.Switch.connect_channel(self.slot, self.channel_number)
		sleep(self.switch_delay)


	def get_cycle_number(self):
		self.cycle_number += 1
		return self.cycle_number


	def sweep(self):
		self.select()
		sweep_result = perform_symmetric_voltage_sweep(self.DMM, self.PSUChannel, self.v_vector, self.delay)
		r_up = sweep_result[0]
		r_down = sweep_result[1]
		return [r_up, r_down]


	def sweep_and_log(self):
		global sweep_counter
		global sweep_buffer

		sweep_result = self.sweep()
		sweep_data = np.vstack([self.v_vector, sweep_result[0], sweep_result[1]])

		# Log directory and file setup
		log_info = self.get_log_file()
		log_dir = log_info[0]
		log_file = log_dir + '/' + log_info[1]

		if not os.path.exists(log_dir):
			os.makedirs(log_dir)

		# Log data locally
		flogger = Flogger(log_file, ',')
		flogger.createFile()
		flogger.logRow(['gate voltage [V]', 'resistance (up) [Ohm]', 'resistance (down) [Ohm]'])
		flogger.logBuffer(sweep_data, axis=1)

		# Plot data
		plt.plot(sweep_data[0], sweep_data[1], label='Up Sweep')
		plt.plot(sweep_data[0], sweep_data[2], label='Down Sweep')
		plt.title(f'Cycle {self.cycle_number}')
		plt.xlabel('Gate Potential (V)')
		plt.ylabel('Resistance (Ohm)')
		plt.legend()

		# Save the plot
		plot_file = os.path.join(log_dir, f'{log_info[1]}_plot.png')
		plt.savefig(plot_file, dpi=300, bbox_inches='tight')
		plt.close()

		# Add the sweep data to the buffer
		sweep_counter += 1
		#sweep_buffer["voltage"].append(sweep_data[0])  # Store voltage data
		resistance_up = sweep_data[1]
		resistance_down = sweep_data[2][::-1][1:-1]
		sweep_buffer["resistance"].append((resistance_up, resistance_down))  # Store resistance data (up and down)
		print('sweep_counter:', sweep_counter)
		# Check if 4 sweeps have been collected
		if sweep_counter == 4:
			# Combine the voltage data
			voltage_up = sweep_data[0]  # 0V to 45V
			voltage_down = voltage_up[::-1][1:-1]  # Flip and exclude the first element (duplicate 45V)
			# combined_voltage = voltage_up + voltage_down
			sweep_buffer["voltage"].append(voltage_up)
			sweep_buffer["voltage"].append(voltage_down)
			
			combined_voltage = np.concatenate(sweep_buffer["voltage"]).tolist()

			# Combine resistance data into separate fields
			resistance_fields = {
				f"resistance_{i+1}": np.concatenate([res[0], res[1]]).tolist()
				for i, res in enumerate(sweep_buffer["resistance"])
			}

			# Add the merged data to the frame buffer
			frame_buffer.generate_measurement_frames(
				sensorhead_name="SensorheadLS",  # Update with the correct name
				receptor=int(self.channel_number/4),
				start_time=datetime.now().timestamp(),
				measurement_data={
					"voltage": combined_voltage,  # Combined voltage
					**resistance_fields            # Resistance fields for all 4 sweeps
				}
			)

			# Attempt to upload data to the database
			try:
				print("Attempting to connect to the database...")
				print("MQTTClient config:", database.__dict__)

				database.connect()
				print('connected to database')

				for frame in frame_buffer.get_frames():
					print("Uploading frame...")
					#print(frame.model_dump_json())  # Debug: Print frame JSON
					database.upload(frame.model_dump_json())
					print('uploaded frame')
					sleep(0.1)  # Throttle upload to avoid overloading the server

				frame_buffer.clear_frames()
				database.disconnect()
				print("Uploaded sweep data to the database successfully.")
			except Exception as e:
				print(f"Failed to upload data to the database: {e}")

			# Reset counter and buffer for the next set of sweeps
			sweep_counter = 0
			sweep_buffer = {"voltage": [], "resistance": []}


	def get_log_file(self):

		t_now = datetime.now()
		date_short = t_now.strftime('%Y-%m-%d')
		date_long = t_now.strftime('%Y-%m-%d-%H-%M-%S')

		cycle_number = self.get_cycle_number()
		
		file_dir = f'{self.log_dir}/ID_{self.identifier}/{date_short}'
		file_name = f'ID_{self.identifier}_{date_long}_{self.comment}_cycle-{cycle_number}.csv'
		return [file_dir, file_name]


# device addresses
DMM_address = 'TCPIP0::192.168.137.164::inst0::INSTR' #DMM_address = 'TCPIP0::192.168.10.71::inst0::INSTR'
PSU_address = 'TCPIP0::192.168.137.63::INSTR' # PSU_address = 'TCPIP0::192.168.10.61::inst0::INSTR'
Switch_address = 'GPIB0::7::INSTR'


# device configuration
DMM = DMM6500(DMM_address)
PSU = DP2031(PSU_address)
# PSU.resource.timeout = 60000
Switch = Switch700X(Switch_address)
v_gate_channel = PSU.channel1

# configure output channels 1 and 2 in series
PSU.set_channel_pairing('SER')
sleep(3)
v_gate_channel.set_output(1)
v_gate_channel.set_voltage_current(0, 0.1)
sleep(3)


#adjust arduino script for additional stabilitation - ethylene
with open(ETHYLENE_ARDUINO_PATH, 'r') as f:
	lines = f.readlines()

lines[0] = f'int additional_stabilization = {additional_stabilization};\n'

with open(ETHYLENE_ARDUINO_PATH, 'w') as f:
	f.writelines(lines)
	
#adjust arduino script for additional stabilitation - humidity
with open(HUMIDITY_ARDUINO_PATH, 'r') as f:
	lines = f.readlines()

lines[0] = f'int additional_stabilization = {additional_stabilization};\n'

with open(HUMIDITY_ARDUINO_PATH, 'w') as f:
	f.writelines(lines)

#flash_arduino(HEATER_ARDUINO_PORT, HEATER_ARDUINO_PATH)
flash_arduino(ETHYLENE_ARDUINO_PORT, ETHYLENE_ARDUINO_PATH)
flash_arduino(HUMIDITY_ARDUINO_PORT, HUMIDITY_ARDUINO_PATH)

# Start air program

subprocess.Popen(['python', ETHYLENE_PROGRAM_PATH, str(additional_stabilization)])
subprocess.Popen(['python', ENVIRONMENTAL_PROGRAM_PATH])

# sweep configuration
v_sweep_start = 0
v_sweep_stop = 1.2
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																									 # half of 50 V because of series output
v_sweep_step = 1e-3 # half of 50 mV because of series output
v_sweep_count = int((v_sweep_stop - v_sweep_start)/v_sweep_step)
v_gate_vector = np.linspace(v_sweep_start, v_sweep_stop, v_sweep_count+1)
psu_delay = 5e-6			# standard is 5e-6

element1_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 1, f'{chip_identifier1}_element 1', f'{conditions1}')
element1_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element1_sweeper.set_log_directory('../logs')

element2_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 2, f'{chip_identifier1}_element 2', f'{conditions1}')
element2_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element2_sweeper.set_log_directory('../logs')

element3_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 3, f'{chip_identifier1}_element 3', f'{conditions1}')
element3_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element3_sweeper.set_log_directory('../logs')

element4_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 4, f'{chip_identifier1}_element 4', f'{conditions1}')
element4_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element4_sweeper.set_log_directory('../logs')

element5_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 5, f'{chip_identifier2}_element 1', f'{conditions2}')
element5_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element5_sweeper.set_log_directory('../logs')

element6_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 6, f'{chip_identifier2}_element 2', f'{conditions2}')
element6_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element6_sweeper.set_log_directory('../logs')

element7_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 7, f'{chip_identifier2}_element 3', f'{conditions2}')
element7_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element7_sweeper.set_log_directory('../logs')

element8_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 8, f'{chip_identifier2}_element 4', f'{conditions2}')
element8_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element8_sweeper.set_log_directory('../logs')

element17_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 9, f'{chip_identifier5}_element 1', f'{conditions5}')
element17_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element17_sweeper.set_log_directory('../logs')

element18_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 10, f'{chip_identifier6}_element 1', f'{conditions6}')
element18_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element18_sweeper.set_log_directory('../logs')

element9_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 11, f'{chip_identifier3}_element 1', f'{conditions3}')
element9_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element9_sweeper.set_log_directory('../logs')

element10_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 12, f'{chip_identifier3}_element 2', f'{conditions3}')
element10_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element10_sweeper.set_log_directory('../logs')

element11_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 13, f'{chip_identifier3}_element 3', f'{conditions3}')
element11_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element11_sweeper.set_log_directory('../logs')

element12_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 14, f'{chip_identifier3}_element 4', f'{conditions3}')
element12_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element12_sweeper.set_log_directory('../logs')

element13_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 15, f'{chip_identifier4}_element 1', f'{conditions4}')
element13_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element13_sweeper.set_log_directory('../logs')

element14_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 16, f'{chip_identifier4}_element 2', f'{conditions4}')
element14_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element14_sweeper.set_log_directory('../logs')

element15_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 17, f'{chip_identifier4}_element 3', f'{conditions4}')
element15_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element15_sweeper.set_log_directory('../logs')

element16_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 18, f'{chip_identifier4}_element 4', f'{conditions4}')
element16_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element16_sweeper.set_log_directory('../logs')

element19_sweeper = GateSweepChannel(DMM, v_gate_channel, Switch, 10, 19, f'{chip_identifier7}_element 1', f'{conditions7}')
element19_sweeper.set_sweep_parameters(v_gate_vector, psu_delay)
element19_sweeper.set_log_directory('../logs')


try:
	while(1):	
		'''element1_sweeper.sweep_and_log()		# In case of parallel measurement on slot 1//drawer 1, only select element1
		element2_sweeper.sweep_and_log()
		element3_sweeper.sweep_and_log()
		element4_sweeper.sweep_and_log()

		element5_sweeper.sweep_and_log()		# In case of parallel measurement on slot 2//drawer 1, only select element5
		element6_sweeper.sweep_and_log()
		element7_sweeper.sweep_and_log()
		element8_sweeper.sweep_and_log()'''

		element9_sweeper.sweep_and_log()		# In case of parallel measurement on slot 3//drawer 1, only select element9
		element10_sweeper.sweep_and_log()
		#element11_sweeper.sweep_and_log()
		#element12_sweeper.sweep_and_log()

		'''element13_sweeper.sweep_and_log()		# In case of parallel measurement on slot 4//drawer 1, only select element13
		element14_sweeper.sweep_and_log()
		element15_sweeper.sweep_and_log()
		element16_sweeper.sweep_and_log()'''

		#element17_sweeper.sweep_and_log()		# Parallel measurement only, slot 2//drawer 2
		#element18_sweeper.sweep_and_log()		# Parallel measurement only, slot 3//drawer 2
		#element19_sweeper.sweep_and_log()		# Parallel measurement only, slot 4//drawer 2



except KeyboardInterrupt:
    print("Keyboard interrupt detected. Exiting...")

# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

finally:
    print("Closing all instrument resources...")
    try:
        DMM.resource.close()
    except Exception as e:
        print(f"Error closing DMM: {e}")
    try:
        Switch.resource.close()
    except Exception as e:
        print(f"Error closing Switch: {e}")
    try:
        PSU.resource.close()
    except Exception as e:
        print(f"Error closing PSU: {e}")
	
