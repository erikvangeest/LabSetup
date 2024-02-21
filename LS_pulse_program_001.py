import numpy as np
from time import sleep
from matplotlib import pyplot as plt
from datetime import datetime
import os


from keithley import DMM6500
from keithley import Switch700X
from rigol import DP2031
from flogger import Flogger


def perform_voltage_sweep(DMM, PSUChannel, v_vector, delay):
	# create buffer for resistance measurements
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
		sweep_result = self.sweep()
		sweep_data = np.vstack([self.v_vector, sweep_result[0], sweep_result[1]])

		log_info = self.get_log_file()
		log_dir = log_info[0]
		log_file = log_dir + '/' + log_info[1]

		if not os.path.exists(log_dir):
			os.makedirs(log_dir)

		flogger = Flogger(log_file, ',')
		flogger.createFile()

		flogger.logRow(['gate voltage [V]', 'resistance (up) [Ohm]', 'resistance (down) [Ohm]'])
		flogger.logBuffer(sweep_data, axis=1)

		plt.plot(sweep_data[0], sweep_data[1])
		plt.plot(sweep_data[0], sweep_data[2])
		
		plt.title(f'Cycle {self.cycle_number}')
		plt.xlabel('Gate Potential (V)')
		plt.ylabel('Resistance (Ohm)')
		
		'''
		plt.show()		#turn on to show the plot for 2 seconds. CAREFUL! This adds 2 seconds between forward and backward sweep and has an effect on the measurement!
		sleep(2)
		plt.close()
		'''
		
		plot_file = os.path.join(log_dir, f'{log_info[1]}_plot.png')	#turn on to save plots in same folder as csv
		plt.savefig(plot_file, dpi=300, bbox_inches='tight')
		plt.close()  

	def get_log_file(self):

		t_now = datetime.now()
		date_short = t_now.strftime('%Y-%m-%d')
		date_long = t_now.strftime('%Y-%m-%d-%H-%M-%S')

		cycle_number = self.get_cycle_number()
		
		file_dir = f'{self.log_dir}/{self.identifier}/{date_short}'
		file_name = f'{self.identifier}_{date_long}_{self.comment}_cycle-{cycle_number}.csv'
		return [file_dir, file_name]


# device addresses
DMM_address = 'TCPIP0::192.168.10.77::inst0::INSTR'
PSU_address = 'TCPIP0::192.168.10.73::inst0::INSTR'
Switch_address = 'GPIB0::7::INSTR'


# device configuration
DMM = DMM6500(DMM_address)
PSU = DP2031(PSU_address)
Switch = Switch700X(Switch_address)
v_gate_channel = PSU.channel1


# configure output channels 1 and 2 in series
PSU.set_channel_pairing('SER')
sleep(3)
v_gate_channel.set_output(1)
v_gate_channel.set_voltage_current(0, 0.1)
sleep(3)


# sweep configuration
v_sweep_start = 0
v_sweep_stop = 40																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																										 # half of 50 V because of series output
v_sweep_step = 100e-3 # half of 50 mV because of series output
v_sweep_count = int((v_sweep_stop - v_sweep_start)/v_sweep_step)
v_gate_vector = np.linspace(v_sweep_start, v_sweep_stop, v_sweep_count+1)
psu_delay = 5e-6			# standard is 5e-6

# log title - experiment information
chip_identifier1 = 	"ID_168" 	# fill in chip number positioned in slot 1
chip_identifier2 = 	"ID_215" 	# fill in chip number positioned in slot 2
chip_identifier3 = 	"ID_208" 	# fill in chip number positioned in slot 3
chip_identifier4 = 	"ID_226" 	# fill in chip number positioned in slot 4
chip_identifier5 = 	"ID_" 	# fill in chip number positioned in slot 5
chip_identifier6 = 	"ID_" 	# fill in chip number positioned in slot 6
chip_identifier7 = 	"ID_" 	# fill in chip number positioned in slot 7

conditions1 = 		"ANL clean drop cast 5x EG004 recryst, par" 		# fill in conditions 1		do not use - sign in the conditions!
conditions2 = 		"ANL clean drop cast 5x EG004 recryst, par" 		# fill in conditions 2
conditions3 = 		"ANL clean drop cast 5x EG004 recryst, par" 		# fill in conditions 3
conditions4 = 		"receptor v2 test in setup" 		# fill in conditions 4
conditions5 = 		"" 		# fill in conditions 5
conditions6 = 		"" 		# fill in conditions 6
conditions7 = 		"" 		# fill in conditions 7

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

while(1):	
	element1_sweeper.sweep_and_log()		# In case of parallel measurement on slot 1//drawer 1, only select element1
	#element2_sweeper.sweep_and_log()
	#element3_sweeper.sweep_and_log()
	#element4_sweeper.sweep_and_log()

	element5_sweeper.sweep_and_log()		# In case of parallel measurement on slot 2//drawer 1, only select element5
	#element6_sweeper.sweep_and_log()
	#element7_sweeper.sweep_and_log()
	#element8_sweeper.sweep_and_log()

	element9_sweeper.sweep_and_log()		# In case of parallel measurement on slot 3//drawer 1, only select element9
	#element10_sweeper.sweep_and_log()
	#element11_sweeper.sweep_and_log()
	#element12_sweeper.sweep_and_log()

	element13_sweeper.sweep_and_log()		# In case of parallel measurement on slot 4//drawer 1, only select element13
	element14_sweeper.sweep_and_log()
	element15_sweeper.sweep_and_log()
	element16_sweeper.sweep_and_log()

	#element17_sweeper.sweep_and_log()		# Parallel measurement only, slot 2//drawer 2
	#element18_sweeper.sweep_and_log()		# Parallel measurement only, slot 3//drawer 2
	#element19_sweeper.sweep_and_log()		# Parallel measurement only, slot 4//drawer 2

	#DMM.resource.close()
	#Switch.resource.close()
	#PSU.resource.close()
	#sleep(1)

