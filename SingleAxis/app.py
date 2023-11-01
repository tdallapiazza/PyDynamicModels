
import sys
# setting path
sys.path.append('../')

import os
import time
import models.BidirectionalConstSpeedAxis as axis
from pymodbus.client import ModbusTcpClient
from flask import Flask, render_template, Response, request, jsonify

app = Flask(__name__)
global axis1, isRunning, isConnected
isRunning = False
isConnected = False
axis1 = axis.BidirectionalConstSpeedAxis(0.01, 0.2, [0.0, 1.8])
axis1.start()


@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/<id>')
def loadPage(id):
    return render_template(id+'.html')

@app.route('/connect', methods=['POST'])
def connect():
    res = False
    global isConnected
    if not('client' in globals()):
        global client
    try:
        if client.connected:
            print("already connected so disconnect")
            client.close()
            del client
            isConnected = False
    except:
        sp=request.form['address'].split(':')
        if len(sp)==1:
            client = ModbusTcpClient(host=sp[0])
        else:
            client = ModbusTcpClient(host=sp[0], port=sp[1])
        print('Connecting to master')
        res=client.connect()
        if res:   
            isConnected = True
        else:
            del client
            isConnected = False
    return {'success': res}

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
    while isConnected:
        res = False
        if 'client' in globals():
            if client.connected:
                res=True
        time.sleep(1.0)
        yield f"data: {res}\n\n"
    yield "data: finished\n\n"

@app.route('/runSim')
def run():
    
    return Response(
        read_state(),  # gen_date_time() is an Iterable
        mimetype='text/event-stream'  # mark as a stream response
    )

# a generator with yield expression
def read_state():
    while isRunning:
        time.sleep(0.01)
        # as we are in simulation, there is no physical inputs so we'll use coils to set interal and read internal values
        # first read model sensors and set the corresponding coils
        ret=''
        if 'client' in globals() and isConnected:
            ad=0
            for output in axis1.digitalOut:
                client.write_coil(ad, output)
                ad+=1
            # then apply the commands if any
            rr = client.read_coils(2,2)
            axis1.run = True if rr.bits[0] else False
            axis1.reverse = True if rr.bits[1] else False
            pos = "%.2f"%axis1.pos
            # formating the response
            ret ='{} {} {} {} {}'.format(pos, axis1.digitalOut[0], axis1.digitalOut[1], axis1.run, axis1.reverse)
            # print(pos, end="   \r", flush=True)
        yield f"data: {ret}\n\n"
    yield "data: finished\n\n"
        
