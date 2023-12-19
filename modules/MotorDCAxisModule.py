from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext
from connectors.modbusConnector import ModbusConnector
from models import motorDCAxisModel as axisModel
import struct

def float_to_int_repr(flo):
    # build the binary representation
    binary = ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', flo))
    # finally return the int representation of that binary in two 16bit registers (Low Word first)
    return [int(binary[16:],2), int(binary[:16],2)]

def registers_to_float(regs):
    #Little Endian low word first
    binary = f'{regs[1]:016b}'+f'{regs[0]:016b}'
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

class MotorDCAxisModule():
    def __init__(self):
        # Setup the connector
        di = ModbusSequentialDataBlock(0x01, [0]*5) #Control buttons (stall, auto/man, start/stop, moveLeft, moveRight)
        ir= ModbusSequentialDataBlock(0x01, float_to_int_repr(0)) #Position as 32bit float
        hr = ModbusSequentialDataBlock(0x01, float_to_int_repr(0)) #Voltage as 32bit float
        self.slaveContext = ModbusSlaveContext(di=di, ir=ir, hr=hr)
        self.connector = ModbusConnector(self.slaveContext)

        # Setup the model
        self.model = axisModel.MotorDCAxisModel()
    
    def update(self):
        # First set input register
        self.connector.args.context[0].setValues(0x04, 0x00, float_to_int_repr(self.model.pos))
        # The digital inputs
        self.connector.args.context[0].setValues(0x02, 0x00, [self.model.stall])

        # then read holding register
        reg = self.connector.args.context[0].getValues(0x03, 0x00, 2)
        self.model.voltage = registers_to_float(reg)
        speed = "%.1f"%self.model.omega
        current = "%.1f"%self.model.current
        temperature ="%d"%self.model.temp
        pos = "%.3f"%self.model.pos
        voltage = "%.1f"%self.model.voltage
        # formating the response
        ret ='{} {} {} {} {}'.format(pos, speed, current, temperature, voltage)
        return ret
    


