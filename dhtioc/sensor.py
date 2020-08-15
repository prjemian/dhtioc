#!/usr/bin/env python3

"""Provide humidity and temperature using EPICS and Raspberry Pi

.. autosummary::
    ~C2F
    ~DHT_IOC
    ~DHT_Sensor
    ~main
    ~run_in_thread
    ~smooth
    ~Trend

"""
# sensor.py
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import adafruit_dht
import atexit
import board
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run as run_ioc
from . import StatsReg
from textwrap import dedent
import threading
import time

INNER_LOOP_SLEEP = 0.01         # s
UPDATE_PERIOD = 2.0             # s, read the DHT22 at this interval (no faster)
RPI_DHT_MODEL = 22              # type of DHT (11, 22, ...)
RPI_DHT_PIN = board.D4          # DHT signal connected to this RPi pin
SMOOTHING_FACTOR = 0.72         # factor between 0 and 1, higher is smoother
TREND_SMOOTHING_FACTOR = 0.95   # applied to the reported trend
# pick smoothing factors: https://github.com/prjemian/dhtioc/issues/20#issuecomment-672074382


def C2F(celsius):
    """convert celsius to fahrenheit"""
    return celsius * 9 / 5 + 32


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def smooth(reading, factor, previous):
    """
    apply smoothing function

    ::

        smoothed = k*raw + (1-k)*previous

    """
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

    .. autosummary::
        ~compute
        ~slope
    """

    def __init__(self):
        self.cache = {k: None for k in [0.8, 0.9, 0.95, 0.98, 0.99]}
        self.stats = StatsReg.StatsRegClass()
        self.trend = None
        self._computed = False

    def compute(self, reading):
        """
        (re)compute the trend

        Actually, reset the stats registers and load new values
        """
        self.stats.Clear()
        self._computed = False
        for factor in self.cache.keys():
            self.cache[factor] = smooth(reading, factor, self.cache[factor])
            self.stats.Add(1-factor, self.cache[factor])

    @property
    def slope(self):
        "set the trend as the slope of smoothed v. (1-smoothing factor)"
        if not self._computed and self.stats.count > 1:
            raw = self.stats.LinearRegression()[-1]
            self.trend = smooth(raw, TREND_SMOOTHING_FACTOR, self.trend)
            self._computed = True
        return self.trend
    
    def __str__(self):
        if self.slope is None:
            return "no trend yet"
        else:
            return "trend: {self.slope:.3f}"



class DHT_Sensor:
    """
    Read from the Digital Humidity & Temperature sensor and cache the raw values

    .. autosummary::
        ~read
        ~read_in_background_thread
    """

    def __init__(self, sensor=None, data_pin=None, update_period=None):
        """
        PARAMETERS

        sensor :
            int
            Always use 22 for now, for a DHT22 sensor.
        data_pin :
            obj
            Such as ``board.D4`` for RPi pin 4.
        update_period :
            float
            Update humidity and temperature at this interval, seconds.
        """
        if sensor not in (22,):
            raise ValueError(f"unexpected sensor value: {sensor}")
        self.pin = data_pin or board.D4
        self.sensor = adafruit_dht.DHT22(self.pin)
        self.update_period = update_period or UPDATE_PERIOD
        self.humidity = None
        self.temperature = None
        self.ready = False
        self.run_permitted = True

        self.read_in_background_thread()
    
    def __str__(self):
        if self.ready:
            return f"RH={self.humidity:.2f}% T={self.temperature:.2f}C"
        else:
            return "no signal yet"

    def read(self):
        """get new raw values from the sensor"""
        try:
            self.temperature = self.sensor.temperature
            self.humidity = self.sensor.humidity
            self.ready = True
        except RuntimeError as exc:
            print(f"{time.time():.2f} {exc}")

    @run_in_thread
    def read_in_background_thread(self):
        "monitor the sensor for new values"
        while self.run_permitted:
            try:
                self.read()
            except Exception as exc:    # anticipate occasional trouble
                print(str(exc))
            time.sleep(self.update_period)


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

    def __init__(self, *args, sensor, data_pin, update_period, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = DHT_Sensor(sensor, data_pin, update_period)
        self.period = update_period
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
        """shutdown the DHT sensor"""
        print(f"stopping DHT sensor")
        self.device.run_permitted = False

    @humidity.startup
    async def humidity(self, instance, async_lib):
        """set the humidity PV"""
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
        """set the humidity:raw PV"""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=self.device.humidity)

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @humidity_trend.startup
    async def humidity_trend(self, instance, async_lib):
        """set the humidity:trend PV"""
        while True:
            if self._set_humidity_trend:
                await instance.write(value=self._humidity_trend.slope)
                self._set_humidity_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature.startup
    async def temperature(self, instance, async_lib):
        """set the temperature PV"""
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
        """set the temperature:raw PV"""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=self.device.temperature)

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_f.startup
    async def temperature_f(self, instance, async_lib):
        """set the temperature:F PV"""
        while True:
            if self._set_temperature_f:
                if self._temperature is not None:
                    await instance.write(value=C2F(self._temperature))
                self._set_temperature_f = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_f_raw.startup
    async def temperature_f_raw(self, instance, async_lib):
        """set the temperature:F:raw PV"""
        t_next_read = time.time()
        while True:
            t_next_read += self.period
            if self.device.ready:
                await instance.write(value=C2F(self.device.temperature))

            while time.time() < t_next_read:
                await async_lib.library.sleep(INNER_LOOP_SLEEP)

    @temperature_trend.startup
    async def temperature_trend(self, instance, async_lib):
        """set the temperature:trend PV"""
        while True:
            if self._set_temperature_trend:
                await instance.write(value=self._temperature_trend.slope)
                self._set_temperature_trend = False
            await async_lib.library.sleep(INNER_LOOP_SLEEP)


def main():
    """entry point for command-line program"""
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='dht:',
        desc=dedent(DHT_IOC.__doc__))
    ioc = DHT_IOC(
        sensor=RPI_DHT_MODEL,
        data_pin=RPI_DHT_PIN,
        update_period=UPDATE_PERIOD,
        **ioc_options)

    def killer(ioc):
        print("deleting IOC object")
        del ioc

    atexit.register(killer, ioc)
    run_ioc(ioc.pvdb, **run_options)


if __name__ == '__main__':
    main()
