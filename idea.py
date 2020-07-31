#!/usr/bin/env python

import numpy
import threading
import time


t0 = time.time()

def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class Actor:

    sample_interval = 2.1   # seconds
    report_interval = 5     # seconds
    sleep_interval = 0.01   # seconds
    scale = 1000
    smoothing = 0.5

    def __init__(self):
        t = time.time()
        self.time_to_sample = t
        self.time_to_report = t
        self.count = 0
        self.run_permitted = True
        self.acquire(first_time=True)

        self.action()

    def report(self):
        # report the value to the listener
        if self.reading is not None:
            print(f"{time.time()-t0:8.3f} {self.count:4d} {self.reading:.2f}")

    def acquire(self, first_time=False):
        # get new value from the input

        # simulated random reading
        v = round(self.scale*numpy.random.rand())

        # simulated random delay time
        time.sleep(numpy.random.rand())

        if first_time:
            self.reading = v
        else:
            self.reading *= self.smoothing
            self.reading += (1-self.smoothing) * v
        self.count += 1

    @run_in_thread
    def action(self):
        while self.run_permitted:
            if time.time() >= self.time_to_sample:
                self.time_to_sample += self.sample_interval
                self.acquire()

            if time.time() >= self.time_to_report:
                self.time_to_report += self.report_interval
                self.report()

            time.sleep(self.sleep_interval)

    def destroy(self):
        self.run_permitted = False
        time.sleep(0.1)


def main():
    actor = Actor()
    time.sleep(15)
    actor.smoothing = 0
    time.sleep(20)
    actor.smoothing = 0.8
    time.sleep(46)
    actor.destroy()


if __name__ == "__main__":
    main()
