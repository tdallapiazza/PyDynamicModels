from threading import Timer
import numpy as np


class BidirectionalConstSpeedAxis(object):
    def __init__(self, dt, speed, sensors=[]):
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
        self.time = 0
        self._timer     = None
        self.dt   = dt
        self.is_running = False
        self.histPos=[]
        self.histTime=[]

        

    def _run(self):
        self.is_running = False
        self.start()

        # time updates
        if self.run:
            if self.reverse:
                self.pos-=self.speed*self.dt
            else:
                self.pos+=self.speed*self.dt
        self.time+=self.dt

        # sensor updates
        for i in range(len(self.sensorsPos)):
            if np.abs(self.pos-self.sensorsPos[i])<=self.detectionRadius:
                self.digitalOut[i]=True
            else:
                self.digitalOut[i]=False

        # History append
        #self.histPos.append(self.pos)
        #self.histTime.append(self.time)


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.dt, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

    def reset(self):
        self.stop()
        self.__init__(self.dt, self.speed, self.sensorsPos)