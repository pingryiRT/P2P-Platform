import threading
import Queue

class Alerter:


    def __init__(self, toUpdate, queue = None):
        if queue is not None:
            queue = Queue.Queue(maxsize=10000)
        self.queue = queue
        self.lock = threading.Lock()
        self.toUpdate = toUpdate

    def update(self, message):
        #TODO add locks here

        self.toUpdate(message)
