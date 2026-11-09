""" Bootloader Request/Response Messages.

    Only client side has been implemented
"""

__all__ = [
    "BootloaderGetCommandsRequest",
    "BootloaderGetVersionRequest",
    "BootloaderGetHardwareVersionRequest",
    "BootloaderGetIdRequest",
    "BootloaderReadMemoryRequest",
    "BootloaderWriteMemoryRequest",
    "BootloaderGoCommandRequest",
    "BootloaderEraseMemoryRequest",
    "BootloaderWriteProtectRequest",
    "BootloaderWriteUnprotectRequest",
    "BootloaderReadoutProtectRequest",
    "BootloaderReadoutUnprotectRequest",
    "BootloaderGetCommandsResponse",
    "BootloaderGetVersionResponse",
    "BootloaderGetHardwareVersionResponse",
    "BootloaderGetIdResponse",
    "BootloaderReadMemoryResponse",
    "BootloaderWriteMemoryResponse",
    "BootloaderGoCommandResponse",
    "BootloaderEraseMemoryResponse",
    "BootloaderWriteProtectResponse",
    "BootloaderWriteUnprotectResponse",
    "BootloaderReadoutProtectResponse",
    "BootloaderReadoutUnprotectResponse"
]

#FIXME fix encoding and decoding of messages

# pylint: disable=missing-type-doc
import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse

# All bootloader modbus request messages
class BootloaderBaseRequest(ModbusRequest):
    _rtu_frame_size = 4

    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
    
    def encode(self):
        # The request has no body
        return b''

class BootloaderGetCommandsRequest(BootloaderBaseRequest):
    function_code = 50
    function_code_name = "bootloader_get_commands"
    
    def __str__(self):
        return "BootloaderGetCommandsRequest"

class BootloaderGetVersionRequest(BootloaderBaseRequest):
    function_code = 51
    function_code_name = "bootloader_get_version"

    def __str__(self):
        return "BootloaderGetVersionRequest"

class BootloaderGetHardwareVersionRequest(BootloaderBaseRequest):
    function_code = 61
    function_code_name = "bootloader_get_hardware_version"

    def __str__(self):
        return "BootloaderGetHardwareVersionRequest"

class BootloaderGetIdRequest(BootloaderBaseRequest):
    function_code = 52
    function_code_name = "bootloader_get_id"

    def __str__(self):
        return "BootloaderGetIdRequest"
    
class BootloaderWriteUnprotectRequest(BootloaderBaseRequest):
    function_code = 58
    function_code_name = "bootloader_write_unprotect"

    def __str__(self):
        return "BootloaderWriteUnprotectRequest"

class BootloaderReadoutProtectRequest(BootloaderBaseRequest):
    function_code = 59
    function_code_name = "bootloader_readout_protect"

    def __str__(self):
        return "BootloaderRedoutProtectRequest"
    
class BootloaderReadoutUnprotectRequest(BootloaderBaseRequest):
    function_code = 60
    function_code_name = "bootloader_readout_unprotect"

    def __str__(self):
        return "BootloaderRedoutUnprotectRequest"

class BootloaderReadMemoryRequest(ModbusRequest):
    function_code = 53
    function_code_name = "bootloader_read_memory"
    _rtu_frame_size = 9

    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
        self.read_address = kwargs.get("read_address", 0x00000000)
        self.read_count = kwargs.get("read_count", 1)
    
    def encode(self):
        result = struct.pack('>I', self.read_address)
        result += struct.pack('>B', self.read_count - 1)
        return result
    
    def __str__(self):
        return "BootloaderReadMemoryRequest"

class BootloaderWriteMemoryRequest(ModbusRequest):
    function_code = 54
    function_code_name = "bootloader_write_memory"
    
    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
        self.write_address = kwargs.get("write_address", 0x00000000)
        self.write_count = kwargs.get("write_count", 1)
        self.data = kwargs.get("data", None)
    
    def encode(self):
        result = struct.pack('>I', self.write_address)
        result += struct.pack('>B', self.write_count - 1)
        for byte in self.data:
            result += struct.pack('>B', byte)
        return result
    
    def __str__(self):
        return "BootloaderWriteMemory"

class BootloaderGoCommandRequest(ModbusRequest):
    function_code = 55
    function_code_name = "bootloader_go_command"

    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
        self.application_address = kwargs.get("application_address", [])

    def encode(self):
        return struct.pack('>I', self.application_address)

    def __str__(self):
        return "BootloaderGoCommandRequest"
    
class BootloaderEraseMemoryRequest(ModbusRequest):
    function_code = 56
    function_code_name = "bootloader_erase_memory"

    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
        self.page_numbers = kwargs.get("page_numbers", [])
    
    def encode(self):
        result = struct.pack('>B', len(self.page_numbers) - 1)
        for page_number in self.page_numbers:
            result += struct.pack('>B', page_number)
        return result

class BootloaderWriteProtectRequest(ModbusRequest):
    function_code = 57
    function_code_name = "bootloader_write_protect"

    def __init__(self, server_address, **kwargs):
        super().__init__(server_address, **kwargs)
        self.sector_codes = kwargs.get("sector_codes", [])
    
    def encode(self):
        result = struct.pack('>B', len(self.sector_codes) - 1)
        for sector_code in self.sector_codes:
            result += struct.pack('>B', sector_code)
        return result

# All bootloader modbus response messages
class BootloaderBaseResponse(ModbusResponse):
    _rtu_frame_size = 4

    def decode(self, data):
        pass

class BootloaderWriteMemoryResponse(BootloaderBaseResponse):
    function_code = 54

    def __str__(self):
        return "BootloaderWriteMemoryResponse"

class BootloaderGoCommandResponse(BootloaderBaseResponse):
    function_code = 55

    def __str__(self):
        return "BootloaderGoCommandResponse"

class BootloaderEraseMemoryResponse(BootloaderBaseResponse):
    function_code = 56

    def __str__(self):
        return "BootloaderEraseMemoryResponse"

class BootloaderWriteProtectResponse(BootloaderBaseResponse):
    function_code = 57

    def __str__(self):
        return "BootloaderWriteProtectResponse"

class BootloaderWriteUnprotectResponse(BootloaderBaseResponse):
    function_code = 58

    def __str__(self):
        return "BootloaderWriteUnprotectResponse"

class BootloaderReadoutProtectResponse(BootloaderBaseResponse):
    function_code = 59

    def __str__(self):
        return "BootloaderReadoutProtectResponse"

class BootloaderReadoutUnprotectResponse(BootloaderBaseResponse):
    function_code = 60

    def __str__(self):
        return "BootloaderReadoutUnprotectResponse"


class BootloaderVariableBaseResponse(ModbusResponse):
    @classmethod
    def calculateRtuFrameSize(cls, buffer):
        data = list(buffer)
        if (len(data) > 2):
            return 3 + data[2] + 1 + 2
        return 0

class BootloaderGetCommandsResponse(BootloaderVariableBaseResponse):
    function_code = 50

    def __init__(self, version=None, commands=None, **kwargs):
        super().__init__(**kwargs)
        self.version = version
        self.commands = commands or []
    
    def decode(self, data):
        self.version = list(data)[1]
        self.commands = list(data)[2:]
    
    def __str__(self):
        return "BootloaderGetCommandsResponse"
    
class BootloaderGetIdResponse(BootloaderVariableBaseResponse):
    function_code = 52

    def __init__(self, id=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id

    def decode(self, data):
        self.id = list(data)[1:]
    
    def __str__(self):
        return "BootloaderGetIdResponse"

class BootloaderReadMemoryResponse(BootloaderVariableBaseResponse):
    function_code = 53

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or []
    
    def decode(self, data):
        self.data = list(data)[1:]
    
    def __str__(self):
        return "BootloaderReadMemoryResponse"

class BootloaderGetVersionResponse(ModbusResponse):
    function_code = 51
    _rtu_frame_size = 5

    def __init__(self, version=None, **kwargs):
        super().__init__(**kwargs)
        self.version = version
    
    def decode(self, data):
        self.version = list(data)[0]
    
    def __str__(self):
        return "BootloaderGetVersionResponse"

class BootloaderGetHardwareVersionResponse(ModbusResponse):
    function_code = 61
    _rtu_frame_size = 5

    def __init__(self, version=None, **kwargs):
        super().__init__(**kwargs)
        self.version = version
    
    def decode(self, data):
        self.version = list(data)[0]
    
    def __str__(self):
        return "BootloaderGetHardwareVersionResponse"