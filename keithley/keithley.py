from instrument import Instrument
from channel import Channel
import pyvisa as visa


class DMM6500(Instrument):


	def __init__(self, resource_address:str):
		self.resource = visa.ResourceManager().open_resource(resource_address)


	def write(self, data):
		self.resource.write(data)


	def query(self, data):
		return self.resource.query(data)


	def save_setup(self, memory_index:int):
		command_string = f'*SAV {memory_index}'
		self.write(command_string)


	def recall_setup(self, memory_index:int):
		command_string = f'*RCL {memory_index}'
		self.write(command_string)


	def measure(self, function, buffer_name:str, buffer_elements):
		buffer_elements_string = ','.join(buffer_elements)
		command_string = f'MEAS:{function}? \"{buffer_name}\", {buffer_elements_string}'
		return self.query(command_string)


	def set_measure_count(self, measure_count:int):
		command_string = f'SENS:COUN {measure_count}'
		self.write(command_string)


	def create_buffer(self, buffer_name:str, buffer_size:int, buffer_style):
		command_string = f'TRAC:MAKE \"{buffer_name}\", {buffer_size}, {buffer_style}'
		self.write(command_string)


	def delete_buffer(self, buffer_name:str):
		command_string = f'TRAC:DEL \"{buffer_name}\"'
		self.write(command_string)


	def set_buffer_mode(self, buffer_name:str, mode:str):
		command_string = f'TRAC:FILL:MODE {mode}, \"{buffer_name}\"'
		self.write(command_string)


	def read_buffer(self, start_index:int, stop_index:int, buffer_name:str, buffer_elements):
		buffer_elements_string = ','.join(buffer_elements)
		command_string = f'TRAC:DATA? {start_index}, {stop_index}, \"{buffer_name}\", {buffer_elements_string}'
		return self.query(command_string)


	def beep(self, frequency:int, duration:float):
		command_string = f'SYST:BEEP {frequency}, {duration}'
		self.write(command_string)


	def set_time(self, year:int, month:int, day:int, hour:int, minute:int, second:int):
		command_string = f'SYST:TIME {year}, {month}, {day}, {hour}, {minute}, {second}'
		self.write(command_string)


	def set_time_local(self):
		from datetime import datetime
		now = datetime.now()
		self.set_time(now.year, now.month, now.day, now.hour, now.minute, now.second)


class Switch700X(Instrument):


	def __init__(self, resource_address:str):
		self.resource = visa.ResourceManager(r"C:\Windows\System32\visa64.dll").open_resource(resource_address)



	def write(self, data):
		self.resource.write(data)


	def query(self, data):
		return self.resource.query(data)


	def disconnect_channel(self, slot, channel):
		command_string = f'ROUT:OPEN (@{slot:02d}!{channel:02d})'
		self.write(command_string)


	def connect_channel(self, slot, channel):
		command_string = f'ROUT:CLOS (@{slot:02d}!{channel:02d})'
		self.write(command_string)


	def disconnect_all(self, slot):
		command_string = 'ROUT:OPEN ALL'
		self.write(command_string)
