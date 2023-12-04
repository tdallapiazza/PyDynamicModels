# deploy using : pyinstaller -c -F --add-data "templates;templates" --add-data "static;static" app.py

import sys

import time
from modules import simpleAxisModule
from flask import Flask, render_template, Response, request, jsonify
from connectors.modbusConnector import ModbusConnector
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
)

app = Flask(__name__)
global module, isRunning, isConnected
module = simpleAxisModule.SimpleAxisModule()

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/<id>')
def loadPage(id):
    return render_template(id+'.html')

@app.route('/connect', methods=['POST'])
def connect():
    global module, isConnected
    sp=request.form['address'].split(':')
    if len(sp)==1:
        module.connector.args.host = sp[0]
    else:
        module.connector.args.host= sp[0]
        module.connector.args.port=sp[1]
    print('Starting the server')
    module.connector.start()
    print('Server started') 
    isConnected = True
    return {'success': True}

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global module, isConnected, isRunning
    if isRunning:
        module.model.stopSim()
        module.model.resetSim()
    if 'module' in globals():
        module.connector.stop()
    print("server stopped")
    isConnected = False
    return {'success': True}

@app.route('/startSim', methods=['POST'])
def startSim():
    module.model.startSim()
    global isRunning
    isRunning=True
    return {'success': True}

@app.route('/stopSim', methods=['POST'])
def stopSim():
    module.model.stopSim()
    global isRunning
    isRunning=False
    return {'success': True}

@app.route('/resetSim', methods=['POST'])
def resetSim():
    module.model.resetSim()
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
    global isRunning, isConnected, module
    while isRunning and isConnected:
        time.sleep(0.01)
        ret = module.update()
        yield f"data: {ret}\n\n"
    yield "data: finished\n\n"
        
@app.route('/ctrlAuto', methods=['POST'])
def setMode():
    global module
    res=False
    if 'module' in globals():
        res=True
        if request.form['data']=='true':
            module.connector.args.context[0].setValues(2, 0x03, [True])
        else:
            module.connector.args.context[0].setValues(2, 0x03, [False])
    return {'success': res}

@app.route('/ctrlRun', methods=['POST'])
def setRun():
    global module
    res=False
    if 'module' in globals():
        res=True
        if request.form['data']=='true':
            module.connector.args.context[0].setValues(2, 0x06, [True])
        else:
            module.connector.args.context[0].setValues(2, 0x06, [False])
    return {'success': res}

@app.route('/ctrlLeft', methods=['POST'])
def setLeft():
    global module
    res=False
    if 'module' in globals():
        res=True
        if request.form['data']=='true':
            module.connector.args.context[0].setValues(2, 0x04, [True])
        else:
            module.connector.args.context[0].setValues(2, 0x04, [False])
    return {'success': res}

@app.route('/ctrlRight', methods=['POST'])
def setRight():
    global module
    res=False
    if 'module' in globals():
        res=True
        if request.form['data']=='true':
            module.connector.args.context[0].setValues(2, 0x05, [True])
        else:
            module.connector.args.context[0].setValues(2, 0x05, [False])
    return {'success': res}

app.run()