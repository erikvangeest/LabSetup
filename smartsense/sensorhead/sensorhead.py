from smartsense.sensorhead.modbus_client import ModbusClient

class Sensorhead:
    ADDRESS_HEATER_TARGET = 1
    ADDRESS_HEATER_TEMPERATURE = 32
    ADDRESS_ENVIRONMENT = 40
    ADDRESS_ENVIRONMENT_RAW = 78
    ADDRESS_ADC = 0
    ADDRESS_ADC_RAW = 62
    ADDRESS_DAC = 0
    ADDRESS_HIGH_VOLTAGE = 0
    ADDRESS_POWER_GOOD = 0
    ADDRESS_CURRENT = 56
    ADDRESS_CURRENT_RAW = 86
    ADDRESS_VOLTAGE = 58
    ADDRESS_VOLTAGE_RAW = 87
    ADDRESS_POWER = 60
    ADDRESS_LED = 1

    def __init__(self, modbus_client: ModbusClient, address = 1):
        self.modbus_client = modbus_client
        self.address = address
    
    def get_address(self):
        return self.address()

    def set_heater_target(self, heater_id, temperature):
        if (heater_id < 1 or heater_id > 4):
            print("Invalid heater ID")
            return
        self.modbus_client.write_single_holding_register_float(self.address, self.ADDRESS_HEATER_TARGET + (heater_id - 1) * 2, temperature)
    
    def set_heater_targets(self, temperature):
        self.modbus_client.write_multiple_holding_registers_float(self.address, self.ADDRESS_HEATER_TARGET, [temperature, temperature, temperature, temperature])

    def get_heater_target(self, heater_id):
        if (heater_id < 1 or heater_id > 4):
            print("Invalid heater ID")
            return
        return self.modbus_client.read_single_holding_register_float(self.address, self.ADDRESS_HEATER_TARGET + (heater_id - 1) * 2)
    
    def get_heater_temperature(self, heater_id):
        if (heater_id < 1 or heater_id > 4):
            print("Invalid heater ID")
            return
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_HEATER_TEMPERATURE + (heater_id - 1) * 2)
    
    def get_full_measurement(self, including_temperature = False):
        len = 16
        if (including_temperature):
            len += 4
        return self.modbus_client.read_input_registers_float(self.address, self.ADDRESS_ADC, len)
    
    def get_full_measurement_raw(self):
        return self.modbus_client.read_input_registers(self.address, self.ADDRESS_ADC_RAW, 16)
    
    def set_gate_voltage(self, value):
        self.set_gate_voltage_raw(int(value / 45 * 65535))

    def set_gate_voltage_raw(self, value):
        self.modbus_client.write_single_holding_register(self.address, self.ADDRESS_DAC, value)
    
    #TODO get_gate_voltage
    
    def set_high_voltage(self, state):
        self.modbus_client.write_single_coil(self.address, self.ADDRESS_HIGH_VOLTAGE, state)

    def get_high_voltage(self):
        return self.modbus_client.read_discrete_input(self.address, self.ADDRESS_POWER_GOOD)
    
    def get_environmental_temperature(self, environment_id):
        if (environment_id < 1 or environment_id > 3):
            print("Invalid environment sensor ID")
            return
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_ENVIRONMENT + (environment_id - 1) * 4)
    
    def get_environmental_temperature_raw(self, environment_id):
        if (environment_id < 1 or environment_id > 3):
            print("Invalid environment sensor ID")
            return
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_ENVIRONMENT_RAW + (environment_id - 1) * 2)
    
    def get_environmental_humidity(self, environment_id):
        if (environment_id < 1 or environment_id > 3):
            print("Invalid environment sensor ID")
            return
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_ENVIRONMENT + 2 + (environment_id - 1) * 4)
    
    def get_environmental_humidity_raw(self, environment_id):
        if (environment_id < 1 or environment_id > 3):
            print("Invalid environment sensor ID")
            return
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_ENVIRONMENT_RAW + 1 + (environment_id - 1) * 2)

    def get_environmental_pressure(self, environment_id):
        if (environment_id != 3):
            print("Pressure only available for environment sensor 3")
            return
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_ENVIRONMENT + 12)
    
    def get_environmental_pressure_raw(self, environment_id):
        if (environment_id != 3):
            print("Pressure only available for environment sensor 3")
            return
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_ENVIRONMENT_RAW + 6)
    
    def get_environmental_voc(self, environment_id):
        if (environment_id != 3):
            print("VOC only available for environment sensor 3")
            return
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_ENVIRONMENT + 14)
    
    def get_environmental_voc_raw(self, environment_id):
        if (environment_id != 3):
            print("VOC only available for environment sensor 3")
            return
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_ENVIRONMENT_RAW + 7)

    def get_full_environmental(self):
        return self.modbus_client.read_input_registers_float(self.address, self.ADDRESS_ENVIRONMENT, 8)

    def get_current(self):
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_CURRENT)
    
    def get_current_raw(self):
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_CURRENT_RAW)
    
    def get_voltage(self):
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_VOLTAGE)
    
    def get_voltage_raw(self):
        return self.modbus_client.read_input_register(self.address, self.ADDRESS_VOLTAGE_RAW)
    
    def get_power(self):
        return self.modbus_client.read_input_register_float(self.address, self.ADDRESS_POWER)

    def set_led(self, led_id, state):
        # The third LED is set in firmware
        if (led_id < 1 or led_id > 2):
            print("Invalid LED ID")
            return
        self.modbus_client.write_single_coil(self.address, self.ADDRESS_LED + led_id - 1, state)

    # These methods are static, as the bootloader is often used without an associated sensorhead object
    @staticmethod
    def bootloader_get_commands(modbus_client: ModbusClient, server_address):
        return modbus_client.bootloader_get_commands(server_address)

    @staticmethod
    def bootloader_get_version(modbus_client: ModbusClient, server_address):
        return modbus_client.bootloader_get_version(server_address)
    
    @staticmethod
    def bootloader_get_hardware_version(modbus_client: ModbusClient, server_address):
        return modbus_client.bootloader_get_hardware_version(server_address)
    
    @staticmethod
    def bootloader_get_id(modbus_client: ModbusClient, server_address):
        return modbus_client.bootloader_get_id(server_address)
    
    @staticmethod
    def bootloader_read_memory(modbus_client: ModbusClient, server_address, address, length):
        return modbus_client.bootloader_read_memory(server_address, address, length)
    
    @staticmethod
    def bootloader_write_memory(modbus_client: ModbusClient, server_address, address, data):
        return modbus_client.bootloader_write_memory(server_address, address, data)
    
    @staticmethod
    def bootloader_go_command(modbus_client: ModbusClient, server_address, address):
        return modbus_client.bootloader_go_command(server_address, address)
    
    @staticmethod
    def bootloader_erase_memory(modbus_client: ModbusClient, server_address, page_numbers):
        return modbus_client.bootloader_erase_memory(server_address, page_numbers)
    
    