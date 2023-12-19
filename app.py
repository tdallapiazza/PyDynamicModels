# deploy using : pyinstaller -c -F --add-data "templates;templates" --add-data "static;static" app.py

import time
from modules import simpleAxisModule, motorDCAxisModule
from flask import Flask, render_template, Response, request

app = Flask(__name__)
global module, isRunning, isConnected
isRunning=False
isConnected=False
#module = simpleAxisModule.SimpleAxisModule()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<mod>/<page>')
def loadPage(mod, page):
    return render_template(mod + "/" + page)

@app.route('/connect', methods=['POST'])
def connect():
    global module, isConnected
    if 'module' in globals():
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
    return {'success': False}

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global module, isConnected, isRunning
    if isRunning:
        module.model.stopSim()
        module.model.resetSim()
    if 'module' in globals():
        module.connector.stop()
        module.__init__()
    print("server stopped")
    isConnected = False
    return {'success': True}

@app.route('/startSim', methods=['POST'])
def startSim():
    if 'module' in globals():
        module.model.startSim()
        global isRunning
        isRunning=True
        return {'success': True}
    return {'success': False}

@app.route('/stopSim', methods=['POST'])
def stopSim():
    if 'module' in globals():
        module.model.stopSim()
        global isRunning
        isRunning=False
        return {'success': True}
    return {'success': False}

@app.route('/resetSim', methods=['POST'])
def resetSim():
    if 'module' in globals():
        module.model.resetSim()
        return {'success': True}
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
        
@app.route('/ctrl', methods=['POST'])
def setMode():
    global module
    res=False
    if 'module' in globals():
        res=True
        cmd = request.form['data']
        eval(cmd)
    return {'success': res}

@app.route('/loadModule', methods=['POST'])
def loadModule():
    global module
    match request.form['data']:
        case "simpleAxisModule":
            print("loading module")
            module = simpleAxisModule.SimpleAxisModule()
        case "motorDCAxisModule":
            print("loading module")
            module = motorDCAxisModule.MotorDCAxisModule()
    return {'success': True}

app.run()