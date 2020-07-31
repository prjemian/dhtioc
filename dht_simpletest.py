#!/usr/bin/env python3

# dht_simpletest.py 
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# https://pinout.xyz/

import adafruit_dht
import board
import datetime
import epics
import time

# Initial the dht device, with data pin connected to:
# dhtDevice = adafruit_dht.DHT22(board.D18)
dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        now = datetime.datetime.now().isoformat(sep=" ")
        print(
            "{}  Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                now, temperature_f, temperature_c, humidity
            )
        )

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        pass  # print(error.args[0])

    time.sleep(2.0)

