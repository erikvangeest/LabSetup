#PS reset
import pyvisa

class DP2031:
    def __init__(self, resource_address):
        self.resource_address = resource_address
        self.rm = None
        self.instrument = None

    def open(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(self.resource_address)

    def close(self):
        if self.instrument is not None:
            self.instrument.close()
        if self.rm is not None:
            self.rm.close()

    def query(self, command):
        if self.instrument is not None:
            return self.instrument.query(command)
        else:
            raise Exception("Instrument not open yet.")

# Usage:

psu = DP2031('TCPIP0::192.168.137.41::INSTR')
try:
    psu.open()
    idn = psu.query('*IDN?')
    print(idn)
finally:
    psu.close()
    print("Connection closed.")