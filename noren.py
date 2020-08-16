#!/usr/bin/env python3

import board
# from dhtioc import DHT_sensor, PIN, READ_PERIOD
from dhtioc import reader


def main():
    # DHT_sensor(PIN, READ_PERIOD)
    reader.main()


if __name__ == "__main__":
    main()
