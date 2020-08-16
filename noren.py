#!/usr/bin/env python3

import board
from dhtioc import DHT_sensor, PIN, READ_PERIOD


def main():
    DHT_sensor(PIN, READ_PERIOD)


if __name__ == "__main__":
    main()
