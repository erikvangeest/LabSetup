from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ModbusResponse, ExceptionResponse
from pymodbus.exceptions import NotImplementedException
import serial.rs485
import smartsense.sensorhead.modbus_bootloader_messages as bootloader

class ModbusClient:
    def __init__(self, port, baudrate):
        self.serial_client = ModbusSerialClient(port, baudrate = baudrate)
        self.serial_client.connect()
        self.serial_client.socket.rs485_mode = serial.rs485.RS485Settings(False, True)
        self.register_bootloader_responses()
    
    def register_bootloader_responses(self):
        self.serial_client.register(bootloader.BootloaderGetCommandsResponse)
        self.serial_client.register(bootloader.BootloaderGetVersionResponse)
        self.serial_client.register(bootloader.BootloaderGetHardwareVersionResponse)
        self.serial_client.register(bootloader.BootloaderGetIdResponse)
        self.serial_client.register(bootloader.BootloaderReadMemoryResponse)
        self.serial_client.register(bootloader.BootloaderWriteMemoryResponse)
        self.serial_client.register(bootloader.BootloaderGoCommandResponse)
        self.serial_client.register(bootloader.BootloaderEraseMemoryResponse)
        self.serial_client.register(bootloader.BootloaderWriteProtectResponse)
        self.serial_client.register(bootloader.BootloaderWriteUnprotectResponse)
        self.serial_client.register(bootloader.BootloaderReadoutProtectResponse)
        self.serial_client.register(bootloader.BootloaderReadoutUnprotectResponse)
    
    def close_connection(self):
        self.serial_client.close()

    def checkResponse(self, response: ModbusResponse):
        if (response.isError()):
            # Response can either be an exception or an exeption response
            # An exception response can not be raised, so we raise a NotImplementedException
            # NotImplementedException because this behaviour is seen when sending a command that is not implemented
            if (type(response) == ExceptionResponse):
                # TODO possibly raise other exception
                raise NotImplementedException
            else:
                raise response

    def read_coils(self, client_address, start_address, num_registers):
        response = self.serial_client.read_coils(start_address, num_registers, client_address)
        self.checkResponse(response)
        coils = []
        #TODO check for multiple bytes
        for i in range(0, num_registers):
            coils.append(response.bits[i])
        return coils
    
    def read_coil(self, client_address, address):
        ret = self.read_coils(client_address, address, 1)
        return ret[0]
    
    def read_discrete_inputs(self, client_address, start_address, num_registers):
        response = self.serial_client.read_discrete_inputs(start_address, num_registers, client_address)
        self.checkResponse(response)
        inputs = []
        #TODO check for multiple bytes
        for i in range(0, num_registers):
            inputs.append(response.bits[i])
        return inputs
    
    def read_discrete_input(self, client_address, address):
        ret = self.read_discrete_inputs(client_address, address, 1)
        return ret[0]
    
    def read_multiple_holding_registers(self, client_address, start_address, num_registers):
        response = self.serial_client.read_holding_registers(start_address, num_registers, client_address)
        self.checkResponse(response)
        return response.registers
    
    def read_single_holding_register(self, client_address, address):
        ret = self.read_multiple_holding_registers(client_address, address, 1)
        return ret[0]

    def read_input_registers(self, client_address, start_address, num_registers):
        response = self.serial_client.read_input_registers(start_address, num_registers, client_address)
        self.checkResponse(response)
        return response.registers
    
    def read_input_register(self, client_address, address):
        ret = self.read_input_registers(client_address, address, 1)
        return ret[0]
    
    def write_single_coil(self, client_address, address, state):
        response = self.serial_client.write_coil(address, state, client_address)
        self.checkResponse(response)
    
    def write_single_holding_register(self, client_address, address, value):
        response = self.serial_client.write_register(address, value, client_address)
        self.checkResponse(response)

    def write_multiple_coils(self, client_address, start_address, states):
        response = self.serial_client.write_coils(start_address, states, client_address)
        self.checkResponse(response)

    def write_multiple_holding_registers(self, client_address, start_address, values):
        response = self.serial_client.write_registers(start_address, values, client_address)
        self.checkResponse(response)

    def float_to_register_array(self, value):
        return ModbusSerialClient.convert_to_registers(value, ModbusSerialClient.DATATYPE.FLOAT32)

    def register_array_to_float(self, array):
        return ModbusSerialClient.convert_from_registers(array, ModbusSerialClient.DATATYPE.FLOAT32)
    
    def read_multiple_holding_registers_float(self, client_address, start_address, num_registers):
        registers = self.read_multiple_holding_registers(client_address, start_address, num_registers * 2)
        if (registers == None):
            return
        values = []
        for i in range(0, num_registers):
            values.append(self.register_array_to_float([registers[i * 2], registers[i * 2 + 1]]))
        return values
    
    def read_single_holding_register_float(self, client_address, address):
        return self.read_multiple_holding_registers_float(client_address, address, 1)[0]
    
    def read_input_registers_float(self, client_address, start_address, num_registers):
        registers = self.read_input_registers(client_address, start_address, num_registers * 2)
        if (registers == None):
            return
        values = []
        for i in range(0, num_registers):
            values.append(self.register_array_to_float([registers[i * 2], registers[i * 2 + 1]]))
        return values
    
    def read_input_register_float(self, client_address, address):
        return self.read_input_registers_float(client_address, address, 1)[0]
    
    def write_single_holding_register_float(self, client_address, address, value):
        self.write_multiple_holding_registers(client_address, address, self.float_to_register_array(value))
    
    def write_multiple_holding_registers_float(self, client_address, start_address, values):
        registers = []
        for value in values:
            registers += self.float_to_register_array(value)
        self.write_multiple_holding_registers(client_address, start_address, registers)
    
    def bootloader_get_commands(self, client_address):
        return self.serial_client.execute(bootloader.BootloaderGetCommandsRequest(client_address))
    
    def bootloader_get_version(self, client_address):
        return self.serial_client.execute(bootloader.BootloaderGetVersionRequest(client_address))
    
    def bootloader_get_hardware_version(self, client_address):
        return self.serial_client.execute(bootloader.BootloaderGetHardwareVersionRequest(client_address))
    
    def bootloader_get_id(self, client_address):
        return self.serial_client.execute(bootloader.BootloaderGetIdRequest(client_address))
    
    def bootloader_read_memory(self, client_address, address, count):
        return self.serial_client.execute(bootloader.BootloaderReadMemoryRequest(client_address, read_address = address, read_count = count))
    
    def bootloader_write_memory(self, client_address, address, data):
        return self.serial_client.execute(bootloader.BootloaderWriteMemoryRequest(client_address, write_address = address, write_count = len(data), data = data))

    def bootloader_go_command(self, client_address, application_address):
        return self.serial_client.execute(bootloader.BootloaderGoCommandRequest(client_address, application_address=application_address))
    
    def bootloader_erase_memory(self, client_address, page_numbers):
        return self.serial_client.execute(bootloader.BootloaderEraseMemoryRequest(client_address, page_numbers=page_numbers))