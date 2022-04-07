import serial.tools.list_ports

basestring = str

class Serial(serial.Serial):
    def port(self, value) -> None: ...
    def from_url(self, url): ...
