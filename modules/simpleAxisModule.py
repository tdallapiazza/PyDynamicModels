from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext
from connectors.modbusConnector import ModbusConnector
from models import simpleAxisModel as axisModel

class SimpleAxisModule():
    def __init__(self):
        # Setup the connector
        di= ModbusSequentialDataBlock(0x01, [0] * 7)
        co = ModbusSequentialDataBlock(0x01, [0] * 2)
        self.slaveContext = ModbusSlaveContext(di=di, co=co)
        self.connector = ModbusConnector(self.slaveContext)

        # Setup the model
        self.model = axisModel.SimpleAxisModel(0.005, 0.3, [0.0, 0.9, 1.8])
    
    def update(self):
        self.connector.args.context[0].setValues(2, 0x00, self.model.digitalOut)

        # then apply the commands if any
        values = self.connector.args.context[0].getValues(1, 0x00, 2)

        self.model.run = True if values[0] else False
        self.model.reverse = True if values[1] else False
        pos = "%.3f"%self.model.pos
        # formating the response
        ret ='{} {} {} {} {} {}'.format(pos, self.model.digitalOut[0], self.model.digitalOut[1],self.model.digitalOut[2], self.model.run, self.model.reverse)
        return ret