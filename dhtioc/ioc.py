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

from .datalogger import DataLogger
from .trend_analysis import SMOOTHING_FACTOR, Trend
from .utils import C2F, smooth

INNER_LOOP_SLEEP = 0.01         # s
REPORT_PERIOD = 2.0             # s, read the DHT22 at this interval (no faster)


class DHT_IOC(PVGroup):
    """
    EPICS server (IOC) with humidity & temperature (read-only) PVs.

    .. autosummary::
        ~shutdown_dht_device
        ~counter
        ~humidity
        ~humidity_raw
        ~humidity_trend
        ~humidity_trend_array
        ~temperature
        ~temperature_raw
        ~temperature_f
        ~temperature_f_raw
        ~temperature_trend
        ~temperature_trend_array
        ~trend_axis

    """

    counter = pvproperty(
        value=0,
        dtype=int,
        read_only=True,
        name='counter',
        doc="counter",
        record='longin')
    humidity = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity',
        doc="relative humidity",
        units="%",
        precision=3,
        record='ai')
    humidity_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity:raw',
        doc="relative humidity: most recent reading",
        units="%",
        precision=1,
        record='ai')
    humidity_trend = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity:trend',
        doc="trend in relative humidity",
        units="a.u.",
        precision=4,
        record='ai')
    humidity_trend_array = pvproperty(
        value=[0,0,0,0,0,0,0,],
        dtype=float,
        read_only=True,
        name='humidity:trend:array',
        doc="relative humidity trend",
        units="%",
        precision=4,
        record='waveform')
    temperature = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature',
        doc="temperature",
        units="C",
        precision=3,
        record='ai')
    temperature_f = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:F',
        doc="temperature",
        units="F",
        precision=3,
        record='ai')
    temperature_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:raw',
        doc="temperature: most recent reading",
        units="C",
        precision=1,
        record='ai')
    temperature_f_raw = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:F:raw',
        doc="temperature: most recent reading",
        units="F",
        precision=1,
        record='ai')
    temperature_trend = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature:trend',
        doc="trend in temperature",
        units="a.u.",
        precision=4,
        record='ai')
    temperature_trend_array = pvproperty(
        value=[0,0,0,0,0,0,0,],
        dtype=float,
        read_only=True,
        name='temperature:trend:array',
        doc="temperature trend",
        units="C",
        precision=4,
        record='waveform')
    trend_axis_array = pvproperty(
        value=[0,0,0,0,0,0,0,],
        dtype=float,
        read_only=True,
        name='trend:raw_fraction',
        doc="fraction of raw data in trend",
        units="a.u.",
        precision=4,
        record='waveform')

    def __init__(self, *args, sensor, report_period, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

        self.device = sensor
        self.period = report_period
        self.prefix = kwargs.get("prefix", "PREFIX NOT PROVIDED")
        self.smoothing = SMOOTHING_FACTOR

        self._humidity = None
        self._humidity_trend = Trend()
        self._temperature = None
        self._temperature_trend = Trend()

        self.datalogger = DataLogger(self.prefix)

        atexit.register(self.device.terminate_background_thread)

    @humidity.startup
    async def humidity(self, instance, async_lib):
        """Set the humidity, temperature and other PVs."""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                rh_raw = self.device.humidity
                self._humidity = smooth(rh_raw, self.smoothing, self._humidity)
                self._humidity_trend.compute(rh_raw)
                await self.humidity_raw.write(value=rh_raw)
                await self.humidity.write(value=self._humidity)
                await self.humidity_trend.write(value=self._humidity_trend.slope)

                keys = sorted(self._humidity_trend.cache.keys())
                arr = [1-factor for factor in keys]
                await self.trend_axis_array.write(value=arr)
                arr = [self._humidity_trend.cache[factor] for factor in keys]
                await self.humidity_trend_array.write(value=arr)

                t_raw = self.device.temperature
                self._temperature = smooth(t_raw, self.smoothing, self._temperature)
                self._temperature_trend.compute(t_raw)
                await self.temperature_raw.write(value=t_raw)
                await self.temperature_f_raw.write(value=C2F(t_raw))
                await self.temperature.write(value=self._temperature)
                await self.temperature_f.write(value=C2F(self._temperature))
                await self.temperature_trend.write(value=self._temperature_trend.slope)

                # assumes same keys for humidity & temperature trends
                arr = [self._temperature_trend.cache[factor] for factor in keys]
                await self.temperature_trend_array.write(value=arr)

                await self.counter.write(value=self.counter.value + 1)

                self.datalogger.record(rh_raw, t_raw)

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)


def main():
    """Entry point for command-line program."""
    from .reader import DHT_sensor, PIN, READ_PERIOD
    import datetime

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='dht:',
        desc=dedent(DHT_IOC.__doc__))

    sensor = DHT_sensor(PIN, READ_PERIOD)
    server = DHT_IOC(sensor=sensor, report_period=REPORT_PERIOD, **ioc_options)

    atexit.register(sensor.terminate_background_thread, server)
    run_ioc(server.pvdb, **run_options)


if __name__ == '__main__':
    main()
