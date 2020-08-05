#!/usr/bin/env python

import datetime
import numpy as np
from ophyd import Component, Device, EpicsSignalRO, Signal
import StatsReg
import time

REPORT_INTERVAL = 5

class MyDhtSignal(Device):

    raw = Component(EpicsSignalRO, "")
    s80 = Component(EpicsSignalRO, ":s80")
    s95 = Component(EpicsSignalRO, ":s95")
    s99 = Component(EpicsSignalRO, ":s99")
    trend = Component(Signal, value=0)
    stats = StatsReg.StatsRegClass()

    def compute(self):
        self.stats.Clear()
        self.stats.Add(1-0.00, self.raw.get())
        self.stats.Add(1-0.80, self.s80.get())
        self.stats.Add(1-0.95, self.s95.get())
        self.stats.Add(1-0.99, self.s99.get())
        a, b = self.stats.LinearRegression()
        self.trend.put(b)


class MyDhtDevice(Device):

    humidity = Component(MyDhtSignal, "humidity")
    temperature = Component(MyDhtSignal, "temperature")

    def compute(self):
        self.humidity.compute()
        self.temperature.compute()


def main():
    rpi = MyDhtDevice("rpib4b1:dht22:", name="rpi")
    rpi.wait_for_connection()

    while True:
        rpi.compute()
        t = round(time.time())
        ts = datetime.datetime.fromtimestamp(t).isoformat()
        print(
            f"{t} {ts}"
            f"   {rpi.humidity.raw.get():.02f}"
            f" {rpi.humidity.trend.get():.05f}"
            f"   {rpi.temperature.raw.get()*9/5+32:.02f}"
            f" {rpi.temperature.raw.get():.02f}"
            f" {rpi.temperature.trend.get():.05f}"
        )
        time.sleep(REPORT_INTERVAL)


if __name__ == "__main__":
    main()
