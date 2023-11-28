from threading import Thread
import asyncio

class ModelInterface(Thread):
    running=False
    loop = asyncio.get_event_loop()

    def __init__(self, integrationTime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = self.run
        self.daemon=True
        self.integrationTime = integrationTime
        self.loop.create_task(self.waitIntegrationCoro, 'waitIntegrationTime')
        
    async def waitIntegrationCoro(self):
        await asyncio.sleep(self.integrationTime)

    def stop(self):
        # Stop the event loop / this will close the thread also
        self.loop.close()
        self.running = False

    def run(self):
        # the target of the thread
        self.running = True
        self.loop.run_forever()
