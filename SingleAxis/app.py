
import sys
# setting path
sys.path.append('../')

import os
import time
import models.BidirectionalConstSpeedAxis as axis
from pymodbus.client import ModbusTcpClient
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/description')
def description():
    return render_template('description.html')

@app.route('/visualisation')
def visu():
    return render_template('visu.html')

@app.route('/runSim')
def run():
    return Response(
        increment(),  # gen_date_time() is an Iterable
        mimetype='text/event-stream'  # mark as a stream response
    )

# a generator with yield expression
def increment():
    count=0
    while True:
        time.sleep(0.005)
        count+=0.1
        # DO NOT forget the prefix and suffix
        yield 'data: %s\n\n' % count