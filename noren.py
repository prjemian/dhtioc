#!/usr/bin/env python3

import board
from dhtioc import DHT_sensor

READ_PERIOD = 2.0
PIN = board.D4


def main():
    DHT_sensor(PIN, READ_PERIOD)


if __name__ == "__main__":
    main()
