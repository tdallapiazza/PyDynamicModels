from time import sleep
from modbusConnector import ModbusConnector
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
)
# Create a slave context
di = ModbusSequentialDataBlock(0x01, [0] * 7)
co = ModbusSequentialDataBlock(0x01, [0] * 2)
slaveContext = ModbusSlaveContext

connector = ModbusConnector(slaveContext)
print("Starting server")
connector.start()
print("Waiting 10s")
sleep(10.0)
print("Stopping server")
connector.stop()
print("Execution finished")