
import sys
# setting path
sys.path.append('../')

import os
import asyncio
import time
import models.BidirectionalConstSpeedAxis as axis
from pymodbus.client import ModbusTcpClient
from flask import Flask, render_template, Response, request, jsonify
from modbusServer import SingleAxisModbusServer

app = Flask(__name__)
global axis1, isRunning, isConnected
isRunning = False
isConnected = False
axis1 = axis.BidirectionalConstSpeedAxis(0.01, 0.2, [0.0, 1.8])
axis1.start()

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/<id>')
def loadPage(id):
    return render_template(id+'.html')

@app.route('/connect', methods=['POST'])
def connect():
    global server, isConnected
    sp=request.form['address'].split(':')
    if len(sp)==1:
        server = SingleAxisModbusServer(host=sp[0])
    else:
        server = SingleAxisModbusServer(host=sp[0], port=sp[1])
    print('Starting the server')
    server.start_server()
    print('Server started') 
    isConnected = True
    return {'success': True}

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global server, isConnected, isRunning
    if isRunning:
        stopSim()
        resetSim()
    if 'server' in globals():
        server.stop_server()
    print("server stopped")
    isConnected = False
    return {'success': True}

@app.route('/startSim', methods=['POST'])
def startSim():
    axis1.start()
    global isRunning
    isRunning=True
    return {'success': True}

@app.route('/stopSim', methods=['POST'])
def stopSim():
    axis1.stop()
    global isRunning
    isRunning=False
    return {'success': True}

@app.route('/resetSim', methods=['POST'])
def resetSim():
    axis1.reset()
    return {'success': True}

@app.route('/checkConnect')
def check_connect():
    return Response(
        connection_checker(),
        mimetype='text/event-stream'
    )
    
def connection_checker():
    global isConnected
    while isConnected:
        time.sleep(0.2)
        yield f"data: {isConnected}\n\n"
    yield "data: finished\n\n"

@app.route('/runSim')
def run():
    
    return Response(
        read_state(),  # gen_date_time() is an Iterable
        mimetype='text/event-stream'  # mark as a stream response
    )

# a generator with yield expression
def read_state():
    while isRunning and isConnected:
        global server
        time.sleep(0.01)
        # as we are in simulation, there is no physical inputs so we'll use coils to set interal and read internal values
        # first read model sensors and set the corresponding coils
        ret='0.0'
        server.args.context[0].setValues(2, 0x00, axis1.digitalOut)

        # then apply the commands if any
        values = server.args.context[0].getValues(1, 0x00, 2)

        axis1.run = True if values[0] else False
        axis1.reverse = True if values[1] else False
        pos = "%.2f"%axis1.pos
        # formating the response
        ret ='{} {} {} {} {}'.format(pos, axis1.digitalOut[0], axis1.digitalOut[1], axis1.run, axis1.reverse)
        # print(pos, end="   \r", flush=True)
        yield f"data: {ret}\n\n"
    yield "data: finished\n\n"
        
