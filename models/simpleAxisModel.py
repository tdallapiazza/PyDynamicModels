from models.modelInterface import ModelInterface

class SimpleAxisModel(ModelInterface):
    reverse = False
    speed = 0.15
    run = False
    pos = 0.0
    time = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(0.005, *args, **kwargs)
        self.loop.addTask(self.integrate, 'integrate')

    async def integrate(self):
        if self.run:
            if self.reverse:
                self.pos-=self.speed*self.integrationTime
            else:
                self.pos+=self.speed*self.integrationTime
        self.time+=self.dt