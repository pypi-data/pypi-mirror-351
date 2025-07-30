from timeit import *
from time import *
from ..science import Duration

MS=1
SEC=1000
SEC_TIME=Duration(1,"s")
MS_TIME=Duration(1,"ms")

class Clock:
    def __init__(self):
        self.time=0
        self.stopped=False
        self.clock_type=None
    
    def down_start(self,msecs:int):
        from threading import Thread
        assert isinstance(msecs,int)
        self.clock_type="down"
        self.stopped=False
        self.time=msecs/1000
        def tick():
            while self.time>0 and not self.stopped:
                self.time-=0.001
                sleep(0.001)
                if self.time==1:
                    self.clock_type=None
        Thread(target=tick).start()
    
    def restart(self):
        self.stopped=False
        if self.clock_type=="down":
            self.down_start(self.time)
        elif self.clock_type=="up":
            self.start()
        if self.time ==0:
            self.clock_type=None
            raise TimeoutError("this clock is not running.")

    def stop(self):
        self.stopped=True

    def clear(self):
        self.time=0
        self.clock_type=None

    def start(self):
        from threading import Thread
        self.clock_type="up"
        def tick():
            while self.time>=0 and not self.stopped:
                self.time+=1
                sleep(0.001)
                if self.time==0:
                    self.clock_type=None
        Thread(target=tick).start()