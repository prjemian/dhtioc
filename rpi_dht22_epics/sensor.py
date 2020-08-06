#!/usr/bin/env python3

# sensor.py
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import adafruit_dht
import board
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run as run_ioc
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

    def __init__(self, *args, data_pin, update_period, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = adafruit_dht.DHT22(data_pin)
        self.period = update_period
        self.smoothing = SMOOTHING_FACTOR

        # internal buffers for signal smoothing
        self._humidity = None
        self._temperature = None
        self._set_temperature_f = False

    @humidity.startup
    async def humidity(self, instance, async_lib):
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            try:
                raw = self.device.humidity
                self._humidity = smooth(raw, self.smoothing, self._humidity)
                await instance.write(value=self._humidity)
            except RuntimeError:
                pass    # DHT's sometimes fail to read, just keep going

            while time.time() < t_next_read:
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
