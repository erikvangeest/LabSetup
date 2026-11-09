from instrument import Instrument
from channel import Channel
import pyvisa as visa


class DP2031(Instrument):


	def __init__(self, resource_address:str):
		self.resource = visa.ResourceManager().open_resource(resource_address)
		self.channel1 = DP2031Channel(self, 'CH1')
		self.channel2 = DP2031Channel(self, 'CH2')
		self.channel3 = DP2031Channel(self, 'CH3')


	def write(self, data):
		self.resource.write(data)


	def query(self, data):
		return self.resource.query(data)


	def identify(self):
		print(self.resource.query('*IDN?'))


	def select_channel(self, channel:int):
		command_string = f'INST:NSEL {channel}'
		self.write(command_string)


	def set_channel_pairing(self, mode:str):
		command_string = f'OUTP:PAIR {mode}'
		self.write(command_string)	


	def measure(self, source):
		command_string = f'MEAS:ALL? {source}'
		measurements = self.query(command_string).split(',')
		voltage = float(measurements[0])
		current = float(measurements[1])
		power = float(measurements[2])
		return [voltage, current, power]



class DP2031Channel(Channel):


	def __init__(self, parent, identifier):
		self.parent = parent
		self.identifier = identifier


	def write(self, data):
		self.parent.write(data)


	def set_voltage_current(self, voltage, current):
		command_string = f':APPL {self.identifier},{voltage},{current}'
		self.write(command_string)


	def get_voltage_current(self):
		return 1


	def select(self):
		command_string = f'INST {self.identifier}'
		self.write(command_string)


	def get_selected(self):
		return 1


	def get_output_mode(self):
		return 1


	def set_ocp(self, state:bool):
		command_string = f':OUTP:OCP {self.identifier},{state}'
		self.write(command_string)


	def get_ocp(self):
		return 1


	def set_ovp(self, state:bool):
		command_string = f':OUTP:OVP {self.identifier},{state}'
		self.write(command_string)


	def get_ovp(self):
		return 1


	def set_output(self, state:bool):
		command_string = f':OUTP {self.identifier},{state}'
		self.write(command_string)


	def get_output(self):
		return 1
