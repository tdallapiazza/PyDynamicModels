from models.modelInterface import ModelInterface
from threading import Thread, Event
from time import sleep, perf_counter
from scipy.integrate import solve_ivp as solve

class MotorDCAxisModel(ModelInterface):
    def __init__(self, dt=0.001):
        self.thread = Thread(target=self.integrate, daemon=True)
        self.dt=dt
        # External parameters
        self.voltage = 0.0
        self.extTorque = 0.0
        self.temp_inf = 20.0

        # Internal parameters
        self.motorFluxConst=0.0772
        self.inductance = 0.00034
        self.resistance = 4.83
        self.frictionFactor = 52e-6 + 0.2e-3 #rotor plus external
        self.inertia = 6.3e-6 + 5e-4 #rotor plus external
        self.heatCapacity = 186
        self.convectionFactor = 2.5
        self.gearRatio = 6.6
        self.pitch = 0.005

        # Updates
        self.pos =0.0
        self.omega=0.0
        self.current=0.0
        self.temp=20
        self.simTime=0
        self.event=Event()
        self.stall = False

    def integrate(self):
        print("Starting thread\n")
        while True:
            sol = solve(self.ode_rhs, (0.0, self.dt), [self.current, self.omega, self.temp, self.pos], )
            self.current = sol.y[0, -1]
            self.omega = sol.y[1, -1]
            self.temp = sol.y[2, -1]
            self.pos = sol.y[3, -1]


            # Sleep or not depends on wall vs sim time
            wait=self.simTime+self.dt-perf_counter()
            if wait >0:
                sleep(wait)
            self.simTime+=self.dt
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
    
    def ode_rhs(self, t, y): #[current, omega, temp]
        ea=self.motorFluxConst*y[1]
        d_current = (self.voltage-self.resistance*y[0]-ea)/self.inductance
        d_omega = (self.motorFluxConst*y[0] - self.frictionFactor*y[1])/self.inertia
        d_temp = (self.resistance*pow(y[0], 2)-self.convectionFactor*(y[2]-self.temp_inf))/self.heatCapacity
        d_pos  = self.pitch*self.omega/self.gearRatio
        return [d_current, d_omega, d_temp, d_pos]

if __name__ == '__main__':
    sim=MotorDCAxisModel()
    sim.startSim()
    sim.voltage=48
    for i in range(0,20):
        if i==10:
            sim.voltage=0
        print("wall time:", perf_counter())
        print("Sim time: ", sim.simTime)
        print("Speed:", sim.omega)
        print("Current", sim.current)
        print("Temperature", sim.temp)
        print("Position:", sim.pos)
        print("---------------")
        sleep(1)
    sim.stopSim()
    print("simulation stopped")