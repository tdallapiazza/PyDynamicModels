from time import sleep
import matplotlib.pyplot as plt
import models.BidirectionalConstSpeedAxis as axis

print("starting...")
axis1 = axis.BidirectionalConstSpeedAxis(0.01, 0.2, [0.0, 1.8])
axis1.start()
plt.axis([0, 10, 0, 1])
try:
    for i in range(0,20):
        # print(rt.v)
        plt.plot(axis1.histTime,axis1.histTime)
        sleep(0.5)

finally:
    axis1.stop() # better in a try/finally block to make sure the program ends!
    print("finished.")
    plt.plot(axis1.histTime,axis1.histTime)