#!/usr/bin/env python3

import logging
import asyncio
from threading import Thread


from pymodbus import __version__ as pymodbus_version
from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer, ServerStop


_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)


class ServerArgs:
    context=None
    identity=None
    port=None
    host=None
    
class SingleSlaveModbusServer():
    def __init__(self, slaveContext, host="localhost", port=5020):

        
        # Steup the server
        self.args = self.setup_server(slaveContext, host, port)
        


    def setup_server(self, slaveContext, host, port):

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

    def run_server(self):
        address = (self.args.host, self.args.port)
        StartTcpServer(
            context=self.args.context,  # Data storage
            identity=self.args.identity,  # server identify
            address=address,  # listen address
        )

    def start_server(self):
        t = Thread(target=self.run_server, daemon=True)
        t.start()
        return True
    
    def stop_server(self):
        ServerStop()
        return True