#!/usr/bin/env python3

"""
Raspberry Pi support to read DHT-22 sensor and update EPICS PVs
"""

import adafruit_dht
import board
import datetime
import epics
import numpy
import os
import sys
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


class EPICS:

    def __init__(self, prefix):
        self.temperature = epics.PV(f"{prefix}temperature")
        self.humidity = epics.PV(f"{prefix}humidity")
        self.ymd = epics.PV(f"{prefix}ymd")
        self.hms = epics.PV(f"{prefix}hms")

    @property
    def connected(self):
        attrs = "temperature humidity ymd hms".split()
        for item in attrs:
            pv = getattr(self, item)
            if not pv.wait_for_connection():
                return False
        return True

    def update(self, temperature, humidity):
        if None in (temperature, humidity):
            return
        t = round(time.time())
        ts = datetime.datetime.fromtimestamp(t)
        ymd, hms = ts.isoformat(sep=" ").split()
        self.ymd.put(ymd)
        self.hms.put(hms)
        self.temperature.put(temperature)
        self.humidity.put(humidity)


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

    def __init__(self, pv_prefix):
        t = time.time()
        self.time_to_sample = t
        self.time_to_report = t
        self.count = 0
        self.run_permitted = True

        self.dht22 = DHT22(board.D4)
        self.pv_prefix = pv_prefix
        if pv_prefix is not None:
            self.pv = EPICS(pv_prefix)
            if not self.pv.connected:
                self.pv = None

        self.temperature = 0
        self.humidity = 0
        self.acquire(first_time=True)
        self.action()

    def report(self):
        if self.pv_prefix is None or self.pv is None:
            self.printed_report()
        else:
            try:
                self.pv.update(self.temperature, self.humidity)
            except Exception as exc:
                print(f"{datetime.datetime.now()} {exc}")

    def printed_report(self):
        # report the value to the listener
        try:
            t = time.time()
            print(
                f"{t:.06f}"
                f"  {datetime.datetime.fromtimestamp(t).isoformat()}"
                f"  {self.count:4d}"
                f"  {self.temperature*9/5+32:.2f}"
                f"  {self.temperature:.2f}"
                f"  {self.humidity:.2f}"
            )
            self.count = 0
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
        except RuntimeError:
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


def get_options():
    import argparse
    parser = argparse.ArgumentParser(
        prog=os.path.split(sys.argv[0])[-1],
        description=__doc__.strip().splitlines()[0],
        )
    parser.add_argument(
        '-p', '--pv_prefix',
        action='store',
        dest='pv_prefix',
        default=None,
        help="EPICS PV prefix, such as 'ioc:dht22:' (default: None)")
    return parser.parse_args()


def main():
    args = get_options()
    actor = Actor(args.pv_prefix)
    time.sleep(15)
    actor.smoothing = 0.8


if __name__ == "__main__":
    main()
