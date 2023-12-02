from models.modelInterface import ModelInterface
from threading import Thread, Event
from time import sleep, perf_counter
import numpy as np

class SimpleAxisModel(ModelInterface):
    def __init__(self, dt, speed, sensors=[]):
        self.thread = Thread(target=self.integrate, daemon=True)
        self.dt=dt
        self.event=Event()
        # Model specific parameters
        self.speed = speed

        # Sensors parameters and state
        self.sensorsPos = sensors
        self.detectionRadius = 0.012
        self.digitalOut = [False for i in range(len(sensors))]


        # Control parameters
        self.run=False
        self.reverse=False

        # Dynamic state and simultation members
        self.pos = 0
        self.simTime=0
        self.is_running = False

    def integrate(self):
        print("Starting thread\n")
        while True:
            self.simTime+=self.dt
            if self.run:
                if self.reverse:
                    self.pos-=self.speed*self.dt
                else:
                    self.pos+=self.speed*self.dt
            # sensor updates
            for i in range(len(self.sensorsPos)):
                if np.abs(self.pos-self.sensorsPos[i])<=self.detectionRadius:
                    self.digitalOut[i]=True
                else:
                    self.digitalOut[i]=False

            # Decide if re-run directly or wait a few to keep sync with wall time
            wait=self.simTime-perf_counter()
            if wait >0:
                sleep(wait)
            
            if self.event.is_set():
                print("Stopping thread")
                break

    def startSim(self):
        self.simTime=perf_counter()
        self.thread.start()

    def stopSim(self):
        self.event.set()
        self.thread.join()
    
    def resetSim(self):
        self.stopSim()
        self.__init__(self.dt, self.speed, self.sensorsPos)

if __name__ == '__main__':
    model=SimpleAxisModel(0.001, 0.1, [0.0, 1.8])
    model.run = True
    model.startSim()
    for i in range(0,10):
        print("Wall / Sim:", perf_counter(), "/", model.simTime)
        print("Effective:", model.pos, "m")
        print("Theoreticaly:", i*0.1, "m")
        sleep(1)
    print("Terminating")
    model.stopSim()
    print("Terminated")