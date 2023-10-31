
import sys
# setting path
sys.path.append('../')

import os
import time
import models.BidirectionalConstSpeedAxis as axis
from pymodbus.client import ModbusTcpClient
from flask import Flask, render_template, Response, request, jsonify

app = Flask(__name__)
global axis1
axis1 = axis.BidirectionalConstSpeedAxis(0.01, 0.2, [0.0, 1.8])
axis1.start()


@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/exercice1')
def ex1():
    return render_template('exercice1.html')

@app.route('/exercice2')
def ex2():
    return render_template('exercice2.html')

@app.route('/connect', methods=['POST', 'GET'])
def connect():
    res = False
    if not('client' in globals()):
        global client
    if request.method == 'POST':
        client = ModbusTcpClient(host=request.form['address'])
        print('Connecting to master')
        res=client.connect()
    return {'success': res}

    
@app.route('/checkConnect')
def check_connect():
    return Response(
        connection_checker(),
        mimetype='text/event-stream'
    )
    

def connection_checker():
    while True:
        if client.connected:
            res=True
        else:
            res=False
        time.sleep(1.0)
        yield f"data: {res}\n\n"

@app.route('/runSim')
def run():
    return Response(
        read_state(),  # gen_date_time() is an Iterable
        mimetype='text/event-stream'  # mark as a stream response
    )

# a generator with yield expression
def read_state():
    while True:
        time.sleep(0.01)
        # as we are in simulation, there is no physical inputs so we'll use coils to set interal and read internal values
        # first read model sensors and set the corresponding coils
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
        