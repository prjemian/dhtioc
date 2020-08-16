#!/usr/bin/env python3

"""Read the sensor and cache the values."""

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
    """Get readings from DH22 sensor."""

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
        if None in (self.humidity, self.temperature):
            return "no signal yet"
        else:
            return f"RH={self.humidity:.1f}% T={self.temperature*9/5+32:.1f}F"

    def read(self):
        try:
            self.temperature = self.sensor.temperature
            self.humidity = self.sensor.humidity
            print(f"{time.time()-self.t0:.2f} {self}")
        except RuntimeError as exc:     # be prepared, it happens too much
            print(f"{time.time()-self.t0:.2f} {exc}")

    @run_in_thread
    def read_in_background_thread(self):
        """monitor the sensor for new values"""
        time_to_read = time.time()
        while self.run_permitted:
            if time.time() >= time_to_read:
                time_to_read += self.period
                self.read()
            time.sleep(LOOP_SLEEP)

    def terminate_background_thread(self):
        self.run_permitted = False


def main():
    DHT_sensor(PIN, READ_PERIOD)


if __name__ == "__main__":
    main()
