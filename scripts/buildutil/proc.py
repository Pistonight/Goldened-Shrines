import time
from buildutil.task import Task
from buildutil.timecode import sec_to_strh

class ProcessHolder:
    def __init__(self):
        self.start_time = None
        self.process = None
        self.task = None
    def is_active(self):
        return self.start_time is not None
    def elapsed_time(self):
        return sec_to_strh(round(time.time()-self.start_time))
    def get_process(self):
        return self.process
    def get_task(self) -> Task:
        return self.task
    def start(self, process, task):
        self.process = process
        self.start_time = time.time()
        self.task = task
        
    def stop(self):
        self.start_time = None
        self.process = None
        self.task = None
