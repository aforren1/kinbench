import serial
from serial.tools import list_ports
import struct

ports = list_ports.comports()

dev_name = next(p.device for p in ports if p.pid == 1155)

dev = serial.Serial(dev_name, 9600, timeout=0.01)
#dev.reset_input_buffer()

while True:
    res = dev.read(64) # read all bytes
    if len(res) > 0:
        res2 = struct.unpack('<' + 'BHH'*10, res[:50]) # convert
        print(res2)
