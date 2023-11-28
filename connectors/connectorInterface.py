from threading import Thread

class ConnectorInterface(Thread):

    running=False

    def configure(self):
        #Do some configuration typically data mapping
        pass

    def stop(self):
        # Close open sockets and stop listening
        pass

    def run(self):
        # The method called in the listening thread
        pass

