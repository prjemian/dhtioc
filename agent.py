#!/usr/bin/env python3

import adafruit_dht
import board
import datetime
import epics
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


class DHT22:
    # https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    # https://pinout.xyz/

    def __init__(self, pin):
        self.device = adafruit_dht.DHT22(pin)

    def read(self):
        temperature_c = self.device.temperature
        humidity = self.device.humidity
        return temperature_c, humidity


class Actor:

    sample_interval = 2.1   # seconds
    report_interval = 5     # seconds
    sleep_interval = 0.01   # seconds
    smoothing = 0.5

    def __init__(self):
        t = time.time()
        self.time_to_sample = t
        self.time_to_report = t
        self.count = 0
        self.run_permitted = True

        self.dht22 = DHT22(board.D4)
        self.acquire(first_time=True)

        self.action()

    def report(self):
        # report the value to the listener
        try:
            print(
                f"{datetime.datetime.now().isoformat(sep=' ')}"
                f" {self.temperature:.2f}"
                f" {self.temperature*9/5+32:.2f}"
                f" {self.humidity:.2f}"
            )
        except Exception:
            pass

    def acquire(self, first_time=False):
        # get new value from the input
        try:
            temperature_c, humidity = self.dht22.read()
            self.count += 1
            if first_time:
                self.temperature = temperature_c
                self.humidity = humidity
            else:
                self.temperature *= self.smoothing
                self.temperature += (1-self.smoothing) * temperature_c
                self.humidity *= self.smoothing
                self.humidity += (1-self.smoothing) * humidity
        except RuntimeError as exc:
            pass

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
    actor.smoothing = 0.8


if __name__ == "__main__":
    main()
