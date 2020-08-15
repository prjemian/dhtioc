#!/usr/bin/env python3

"""RPi support to read DHT-22 sensor and update EPICS PVs"""

import adafruit_dht
import board
import datetime
import epics
import numpy
import os
import StatsReg
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


def smooth_it(base, factor, reading):
    return factor * base + (1-factor) * reading


def compute_slope(x, y):
    stats = StatsReg.StatsRegClass()
    stats.Clear()
    for a, b in zip(x, y):
        stats.Add(a, b)
    return stats.slope()


class EPICS:

    def __init__(self, prefix):
        self.temperature = epics.PV(f"{prefix}temperature")
        self.temperature_trend = epics.PV(f"{prefix}temperature:trend")
        self.humidity = epics.PV(f"{prefix}humidity")
        self.humidity_trend = epics.PV(f"{prefix}humidity:trend")
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

    def update(self, temperature, humidity, t_trend=None, rh_trend=None):
        if None in (temperature, humidity):
            return
        t = round(time.time())
        ts = datetime.datetime.fromtimestamp(t)
        ymd, hms = ts.isoformat(sep=" ").split()
        self.ymd.put(ymd)
        self.hms.put(hms)
        self.temperature.put(temperature)
        self.humidity.put(humidity)
        if t_trend is not None:
            self.temperature_trend.put(t_trend)
        if rh_trend is not None:
            self.humidity_trend.put(rh_trend)


class DHT22:
    # https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    # https://pinout.xyz/

    def __init__(self, pin):
        """constructor"""
        self.device = adafruit_dht.DHT22(pin)
        # array of smoothing factors
        self.k_arr = [0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99]
        self.T_arr = None
        self.RH_arr = None

    def read(self):
        temperature_c = self.device.temperature
        humidity = self.device.humidity

        def updater(k_arr, arr, value):
            return [
                smooth_it(arr[i], k, value)
                for i, k in enumerate(k_arr)
            ]

        if self.T_arr is None:
            self.T_arr = [temperature_c for i in self.k_arr]
            T_trend = 0
        else:
            self.T_arr = updater(self.k_arr, self.T_arr, temperature_c)
            T_trend = compute_slope(self.k_arr, self.T_arr)

        if self.RH_arr is None:
            self.RH_arr = [humidity for i in self.k_arr]
            RH_trend = 0
        else:
            self.RH_arr = updater(self.k_arr, self.RH_arr, humidity)
            RH_trend = compute_slope(self.k_arr, self.RH_arr)

        return dict(
            T=temperature_c,
            T_trend=T_trend,
            RH=humidity,
            RH_trend=RH_trend,
        )


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
        if self.pv_prefix is not None and self.pv is not None:
            try:
                # TODO: trends
                self.pv.update(self.temperature, self.humidity)
            except Exception as exc:
                print(f"{datetime.datetime.now()} {exc}")
        self.printed_report()

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
            sensor = self.dht22.read()
            self.count += 1
            # TODO: trends
            if first_time:
                self.temperature = sensor["T"]
                self.humidity = sensor["RH"]
            else:
                self.temperature = smooth_it(
                    self.temperature, self.smoothing, sensor["T"])
                self.humidity = smooth_it(
                    self.humidity, self.smoothing, sensor["RH"])
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
