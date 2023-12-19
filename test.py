from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusServerContext
from pymodbus.server import StartTcpServer
from pymodbus import __version__ as pymodbus_version
import numpy
import struct
from time import sleep
from threading import Thread
import random


class ServerArgs:
    context=None
    identity=None
    port=None
    host=None

def float_to_int_repr(flo):
    # build the binary representation
    binary = ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', flo))
    # finally return the int representation of that binary in two 16bit registers (Low Word first)
    return [int(binary[16:],2), int(binary[:16],2)]

def registers_to_float(regs):
    #Little Endian low word first
    binary = f'{regs[1]:016b}'+f'{regs[0]:016b}'
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

my_float = 50.1230049133
print(float_to_int_repr(my_float))

ir= ModbusSequentialDataBlock(0x01, float_to_int_repr(0) )
hr= ModbusSequentialDataBlock(0x01, float_to_int_repr(0) )
slaveContext = ModbusSlaveContext(ir=ir, hr=hr)
serverContext = ModbusServerContext(slaves=slaveContext, single=True)
identity = ModbusDeviceIdentification(
    info_name={
        "VendorName": "Pymodbus",
        "ProductCode": "PM",
        "VendorUrl": "DyMation",
        "ProductName": "Pymodbus Server",
        "ModelName": "Pymodbus Server",
        "MajorMinorRevision": pymodbus_version,
    }
)
args = ServerArgs()
args.context = serverContext
args.identity = identity
args.port=5020
args.host="127.0.0.2"


def runServer():
    StartTcpServer(
        context=args.context,  # Data storage
        identity=args.identity,  # server identify
        address=(args.host, args.port)  # listen address
    )
thread = Thread(target = runServer, daemon=True)
thread.start()


print("Started")
value = 0.0
try:
    while True:
        value = random.uniform(0.0, 1.2)
        args.context[0].setValues(0x04, 0x00, float_to_int_repr(value))
        holdingReg = args.context[0].getValues(0x03, 0x00, 2)
        registers_to_float(holdingReg)
        sleep(5)
except KeyboardInterrupt:
    print('interrupted!')