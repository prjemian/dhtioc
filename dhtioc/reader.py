#!/usr/bin/env python3

__all__ = "DHT_sensor PIN READ_PERIOD".split()

"""Read the sensor and cache the values.

.. autosummary::
    ~DHT_sensor
    ~main

"""

import adafruit_dht
import atexit
import board
import logging
import time
from .utils import run_in_thread

logger = logging.getLogger(__name__)
LOOP_SLEEP = 0.02
READ_PERIOD = 2.0
PIN = board.D4


class DHT_sensor:
    """
    Get readings from DH22 sensor.

    .. autosummary::
        ~read
        ~read_in_background_thread
        ~ready
        ~terminate_background_thread

    """

    def __init__(self, pin, period):
        """
        Connect with DHT22 sensor and read values

        PARAMETERS

        pin :
            *object*
            RPi pin to which DHT22 signal is connected,
            instance of ``board.Pin``.
        period :
            *float*
            Try to read the sensor every ``period`` seconds.

        """
        self.sensor = adafruit_dht.DHT22(pin)
        self.period = period
        self.temperature = None
        self.humidity = None
        self.t0 = time.time()
        self.run_permitted = True
        atexit.register(self.terminate_background_thread)

        self.read_in_background_thread()

    def __str__(self):
        """Default string."""
        if self.ready:
            return f"RH={self.humidity:.1f}% T={self.temperature*9/5+32:.1f}F"
        else:
            return "no signal yet"

    def read(self):
        """Read signals from the DHT22 sensor."""
        try:
            self.temperature = self.sensor.temperature
            self.humidity = self.sensor.humidity
            logger.info(f"{time.time()-self.t0:.2f} {self}")
        except Exception as exc:     # be prepared, it happens too much
            logger.debug(f"{time.time()-self.t0:.2f} {exc}")

    @run_in_thread
    def read_in_background_thread(self):
        """Monitor the sensor for new values."""
        time_to_read = time.time()
        while self.run_permitted:
            if time.time() >= time_to_read:
                time_to_read += self.period
                self.read()
            time.sleep(LOOP_SLEEP)

    @property
    def ready(self):
        """Has a value been read for both humidity and temperature?"""
        return None not in (self.humidity, self.temperature)

    def terminate_background_thread(self, *args, **kwargs):
        """Signal the background thread to stop."""
        logger.debug("terminate background thread")
        self.run_permitted = False
        time.sleep(LOOP_SLEEP*4)


def main():
    """Development use only."""
    sensor = DHT_sensor(PIN, READ_PERIOD)
    t0 = time.time()
    while True:
        print(f"{time.time()-t0:.2f} {sensor}")
        time.sleep(2)


if __name__ == "__main__":
    main()
