from connectors.connectorInterface import ConnectorInterface
from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus import __version__ as pymodbus_version
from pymodbus.server import StartTcpServer, ServerStop

class ServerArgs:
    context=None
    identity=None
    port=None
    host=None


class ModbusConnector(ConnectorInterface):
    def __init__(self, slaveContext, *args, host="localhost", port=5020, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = self.setup(slaveContext, host, port)
        self.target = self.run
        self.daemon=True
    def setup(self, slaveContext, host, port):

        # Build data storage
        context = ModbusServerContext(slaves=slaveContext, single=True)

        # ----------------------------------------------------------------------- #
        # initialize the server information
        # ----------------------------------------------------------------------- #
        # If you don't set this or any fields, they are defaulted to empty strings.
        # ----------------------------------------------------------------------- #
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
        args.context = context
        args.identity = identity
        args.port=port
        args.host=host
        return args
    
    def run(self):
        self.running = True
        address = (self.args.host, self.args.port)
        StartTcpServer(
            context=self.args.context,  # Data storage
            identity=self.args.identity,  # server identify
            address=address,  # listen address
        )

    def stop(self):
        ServerStop()