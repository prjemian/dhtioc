#!/usr/bin/env python3

# sensor.py
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import adafruit_dht
import board
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import datetime
from textwrap import dedent
import time

UPDATE_PERIOD = 2.0 # s, read the DHT22 at this interval (no faster)
RPI_PIN_DHT22 = board.D4    # DHT22 signal on this RPi pin


class DHT22_IOC(PVGroup):
    """
    EPICS server (IOC) with humidity & temperature (read-only) PVs
    """

    humidity = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='humidity',
        doc="relative humidity (%)",
        record='ai')
    temperature = pvproperty(
        value=0,
        dtype=float,
        read_only=True,
        name='temperature',
        doc="temperature (C)",
        record='ai')

    def __init__(self, *args, data_pin, update_period, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = adafruit_dht.DHT22(data_pin)
        self.period = update_period

    @humidity.startup
    async def humidity(self, instance, async_lib):
        while True:
            try:
                v = self.device.humidity
                await instance.write(value=v)
            except RuntimeError:
                pass    # DHT's sometimes fail to read, just keep going
            await async_lib.library.sleep(self.period)

    @temperature.startup
    async def temperature(self, instance, async_lib):
        while True:
            try:
                v = self.device.temperature
                await instance.write(value=v)
            except RuntimeError:
                pass    # DHT's sometimes fail to read, just keep going
            await async_lib.library.sleep(self.period)


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='dht22:',
        desc=dedent(DHT22_IOC.__doc__))
    ioc = DHT22_IOC(
        data_pin=RPI_PIN_DHT22, 
        update_period=UPDATE_PERIOD, 
        **ioc_options)
    run(ioc.pvdb, **run_options)
