from time import sleep
import models.BidirectionalConstSpeedAxis as axis
from pymodbus.client import ModbusTcpClient

print("Starting simulated model thread.")
axis1 = axis.BidirectionalConstSpeedAxis(0.01, 0.2, [0.0, 1.8])
axis1.start()
plt.axis([0, 10, 0, 1])

print("Connecting to PLC.")
client = ModbusTcpClient(host='localhost')
client.connect()


try:
    print("Running simulation loop. Press Ctl-c to terminate.")
    while True:
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
        print("%.2f"%axis1.pos, end="   \r", flush=True)
        sleep(0.01)
except KeyboardInterrupt:
    axis1.stop() # stop model thread
    client.close() # close modbus PCL connection
    print("Model thread stopped and simulation loop terminated.")