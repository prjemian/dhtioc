#!/usr/bin/env python3

"""
Provide humidity and temperature using EPICS and Raspberry Pi

.. autosummary::
    ~DHT_IOC
    ~main

"""
# sensor.py
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import atexit
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run as run_ioc
from textwrap import dedent
import time

from .trend_analysis import SMOOTHING_FACTOR, Trend
from .utils import C2F, smooth

INNER_LOOP_SLEEP = 0.01         # s
REPORT_PERIOD = 2.0             # s, read the DHT22 at this interval (no faster)


class DHT_IOC(PVGroup):
    """
    EPICS server (IOC) with humidity & temperature (read-only) PVs

    .. autosummary::
        ~shutdown_dht_device
        ~humidity
        ~humidity_raw
        ~humidity_trend
        ~temperature
        ~temperature_raw
        ~temperature_f
        ~temperature_f_raw
        ~temperature_trend
    """

    humidity = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity',
        doc="relative humidity",
        units="%",
        record='ai')
    humidity_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity:raw',
        doc="relative humidity: most recent reading",
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
    temperature_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:raw',
        doc="temperature: most recent reading",
        units="C",
        record='ai')
    temperature_f_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:F:raw',
        doc="temperature: most recent reading",
        units="F",
        record='ai')
    temperature_trend = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:trend',
        doc="trend in temperature",
        record='ai')

    def __init__(self, *args, sensor, report_period, **kwargs):
        """constructor"""
        super().__init__(*args, **kwargs)
        self.device = sensor
        self.period = report_period
        self.smoothing = SMOOTHING_FACTOR

        # internal buffers for trending & signal smoothing
        self._humidity = None
        self._humidity_trend = Trend()
        self._set_humidity_trend = False

        self._temperature = None
        self._temperature_trend = Trend()
        self._set_temperature_f = False
        self._set_temperature_trend = False

        atexit.register(self.shutdown_dht_device)

    def shutdown_dht_device(self):
        """Shutdown the DHT sensor."""
        print("stopping DHT sensor")
        self.device.run_permitted = False

    @humidity.startup
    async def humidity(self, instance, async_lib):
        """Set the humidity PV."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                raw = self.device.humidity
                self._humidity = smooth(raw, self.smoothing, self._humidity)
                await instance.write(value=self._humidity)
                self._humidity_trend.compute(raw)
                self._set_humidity_trend = True

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @humidity_raw.startup
    async def humidity_raw(self, instance, async_lib):
        """Set the humidity:raw PV."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=self.device.humidity)

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @humidity_trend.startup
    async def humidity_trend(self, instance, async_lib):
        """Set the humidity:trend PV."""
        while True:
            if self._set_humidity_trend:
                await instance.write(value=self._humidity_trend.slope)
                self._set_humidity_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature.startup
    async def temperature(self, instance, async_lib):
        """Set the temperature PV."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                raw = self.device.temperature
                self._temperature = smooth(raw, self.smoothing, self._temperature)
                await instance.write(value=self._temperature)
                self._temperature_trend.compute(raw)
                self._set_temperature_trend = True
                self._set_temperature_f = True

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_raw.startup
    async def temperature_raw(self, instance, async_lib):
        """Set the temperature:raw PV."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=self.device.temperature)

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_f.startup
    async def temperature_f(self, instance, async_lib):
        """Set the temperature:F PV."""
        while True:
            if self._set_temperature_f:
                if self._temperature is not None:
                    await instance.write(value=C2F(self._temperature))
                self._set_temperature_f = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_f_raw.startup
    async def temperature_f_raw(self, instance, async_lib):
        """Set the temperature:F:raw PV."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=C2F(self.device.temperature))

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_trend.startup
    async def temperature_trend(self, instance, async_lib):
        """Set the temperature:trend PV."""
        while True:
            if self._set_temperature_trend:
                await instance.write(value=self._temperature_trend.slope)
                self._set_temperature_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)


class MyIoc(PVGroup):

    humidity = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity',
        doc="relative humidity",
        units="%",
        record='ai')

    temperature = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature',
        doc="temperature",
        units="C",
        record='ai')

    def __init__(self, *args, sensor, update_period, **kwargs):
        self.device = sensor
        self.period = update_period
        self.smoothing = SMOOTHING_FACTOR

        atexit.register(self.device.terminate_background_thread)

    def updater(self):
        time_to_update_pvs = time.time()
        while True:
            if time.time() >= time_to_update_pvs:
                time_to_update_pvs += self.period
                print(f"{time.time():.2f} {self.device}")
                if None not in (self.device.humidity, self.device.temperature):
                    self.humidity.write(self.humidity.temperature)
                    self.temperature.write(self.device.temperature)
            time.sleep(0.02)


def main():
    """Entry point for command-line program."""
    from .reader import DHT_sensor, PIN, READ_PERIOD

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='dht:',
        desc=dedent(DHT_IOC.__doc__))

    sensor = DHT_sensor(PIN, READ_PERIOD)
    server = MyIoc(sensor=sensor, report_period=REPORT_PERIOD, **ioc_options)

    def killer(server):
        print("deleting IOC object")
        del server

    atexit.register(killer, server)
    run_ioc(server.pvdb, **run_options)


if __name__ == '__main__':
    main()
