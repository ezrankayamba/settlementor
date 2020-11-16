import time
import threading


class Processor(threading.Thread):
    def __init__(self,  **kwargs):
        super(Processor, self).__init__(**kwargs)

    def run(self):
        time.sleep(10)
        print('Done processing the file')
