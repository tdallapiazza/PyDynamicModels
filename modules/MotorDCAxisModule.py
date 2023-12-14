from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext
from connectors.modbusConnector import ModbusConnector
from models import motorDCAxisModel as axisModel

class MotorDCAxisModule():
    def __init__(self):
        # Setup the connector
        ir= ModbusSequentialDataBlock(0x01, [0] * 1)
        hr = ModbusSequentialDataBlock(0x01, [0] * 1)
        self.slaveContext = ModbusSlaveContext(ir=ir, hr=hr)
        self.connector = ModbusConnector(self.slaveContext)

        # Setup the model
        self.model = axisModel.MotorDCAxisModel()
    
    def update(self):
        self.connector.args.context[0].setValues(1, 0x00, self.model.pos)

        # then apply the commands if any
        values = self.connector.args.context[0].getValues(1, 0x00, 1)

        self.model.voltage = values[0]
        speed = "%.3f"%self.model.omega
        current = "%.3f"%self.model.current
        temperature ="%.3f"%self.model.temp
        pos = "%.3f"%self.model.pos
        # formating the response
        ret ='{} {} {} {}'.format(pos, speed, current, temperature)
        return ret