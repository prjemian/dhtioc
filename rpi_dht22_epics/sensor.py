#!/usr/bin/env python3

# sensor.py
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import Adafruit_DHT
import board
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run as run_ioc
import StatsReg
from textwrap import dedent
import time

INNER_LOOP_SLEEP = 0.01  # s
UPDATE_PERIOD = 2.0 # s, read the DHT22 at this interval (no faster)
RPI_PIN_DHT22 = board.D4    # DHT22 signal on this RPi pin
SMOOTHING_FACTOR = 0.6     # factor between 0 and 1, higher is smoother


def smooth(reading, factor, previous):
    if previous is None:
        value = reading
    else:
        value = factor*previous + (1-factor)*reading
    return value


class Trend:
    """
    Compute the current trend in signal values

    Apply smoothing with various factors, and take the slope
    of the smoothed signal v. the smoothing factor.
    """

    def __init__(self):
        self.cache = {k: None for k in [0.8, 0.9, 0.95, 0.98, 0.99]}
        self.stats = StatsReg.StatsRegClass()
        self.trend = None

    def compute(self, reading):
        self.stats.Clear()
        for factor in self.cache.keys():
            self.cache[factor] = smooth(reading, factor, self.cache[factor])
            self.stats.Add(1-factor, self.cache[factor])

    @property
    def slope(self):
        raw = self.stats.LinearRegression()[-1]
        self.trend = smooth(raw, 0.999, self.trend)
        return self.trend


class DHT22_IOC(PVGroup):
    """
    EPICS server (IOC) with humidity & temperature (read-only) PVs
    """

    humidity = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity',
        doc="relative humidity",
        units="%",
        record='ai')
    humidity_trend = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity:trend',
        doc="trend in relative humidity",
        record='ai')
    temperature = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature',
        doc="temperature",
        units="C",
        record='ai')
    temperature_f = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:F',
        doc="temperature",
        units="F",
        record='ai')
    temperature_trend = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:trend',
        doc="trend in temperature",
        record='ai')

    def __init__(self, *args, data_pin, update_period, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = adafruit_dht.DHT22(data_pin)
        self.period = update_period
        self.smoothing = SMOOTHING_FACTOR
        self.trend_smoothing = 0.995    # reduces noise

        # internal buffers for trending & signal smoothing
        self._humidity = None
        self._humidity_trend = Trend()
        self._set_humidity_trend = False

        self._temperature = None
        self._temperature_trend = Trend()
        self._set_temperature_f = False
        self._set_temperature_trend = False

    @humidity.startup
    async def humidity(self, instance, async_lib):
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            try:
                raw = self.device.humidity
                self._humidity = smooth(raw, self.smoothing, self._humidity)
                await instance.write(value=self._humidity)
                self._humidity_trend.compute(raw)
                self._set_humidity_trend = True
            except RuntimeError:
                pass    # DHT's sometimes fail to read, just keep going

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @humidity_trend.startup
    async def humidity_trend(self, instance, async_lib):
        while True:
            if self._set_humidity_trend:
                await instance.write(value=self._humidity_trend.slope)
                self._set_humidity_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature.startup
    async def temperature(self, instance, async_lib):
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            try:
                raw = self.device.temperature
                self._temperature = smooth(raw, self.smoothing, self._temperature)
                await instance.write(value=self._temperature)
                self._temperature_trend.compute(raw)
                self._set_temperature_trend = True
                self._set_temperature_f = True
            except RuntimeError:
                pass    # DHT's sometimes fail to read, just keep going

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_f.startup
    async def temperature_f(self, instance, async_lib):
        while True:
            if self._set_temperature_f:
                if self._temperature is not None:
                    await instance.write(value=self._temperature*9/5+32)
                self._set_temperature_f = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_trend.startup
    async def temperature_trend(self, instance, async_lib):
        while True:
            if self._set_temperature_trend:
                await instance.write(value=self._temperature_trend.slope)
                self._set_temperature_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)


def main():
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='dht22:',
        desc=dedent(DHT22_IOC.__doc__))
    ioc = DHT22_IOC(
        data_pin=RPI_PIN_DHT22,
        update_period=UPDATE_PERIOD,
        **ioc_options)
    run_ioc(ioc.pvdb, **run_options)


if __name__ == '__main__':
    main()
