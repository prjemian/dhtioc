#!/usr/bin/env python3

__all__ = ["DataLogger",]

"""
Record raw values in data files.

.. autosummary::
    ~DataLogger

"""

import datetime
import logging
import os
import time

logger = logging.getLogger(__name__)

class DataLogger:
    """
    Record raw values in data files.

    PARAMETERS

    ioc_prefix
        *str* :
        EPICS IOC prefix
    path
        *str* :
        Base directory path under which to store data files.
        (default: ``~/Documents/dhtioc_raw``)
    """

    def __init__(self, ioc_prefix, path=None):
        """Constructor."""
        self.prefix = ioc_prefix
        self.base_path = path or os.path.abspath(
            os.path.join(
                os.environ.get("HOME", os.path.join("/", "home", "pi")),
                "Documents",
                "dhtioc_raw"
            )
        )
        self.file_extension = "txt"

    def get_daily_file(self, when=None):
        """
        Return absolute path to daily file.

        PARAMETERS

        when
            *obj* :
            Path will be based on this instance of `datetime.datetime`.
            (default: now)
        """
        dt = when or datetime.datetime.now()
        path = os.path.join(
            self.base_path,
            f"{dt.year:04d}",
            f"{dt.month:02d}",
            (
                f"{dt.year:04d}"
                f"-{dt.month:02d}"
                f"-{dt.day:02d}"
                f".{self.file_extension}"
            ),
        )
        return path

    def create_file(self, fname):
        """
        Create the data file (and path as necessary)

        PARAMETERS

        fname
            *str* :
            File to be created.  Absolute path.
        """
        path = os.path.split(fname)[0]

        # create path as needed
        os.makedirs(path, exist_ok=True)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Could not create directory path: {path}")

        # create file
        with open(fname, "w") as f:
            created = datetime.datetime.now().isoformat(sep=" ")
            f.write(
                f"# file: {fname}\n"
                f"# created: {created}\n"
                f"# program: dhtioc\n"
                f"# URL: https://dhtioc.readthedocs.io/\n"
                f"#\n"
                f"# IOC prefix: {self.prefix}\n"
                f"#\n"
                f"# time: python timestamp (``time.time()``),"  # long line ...
                f" seconds (since 1970-01-01T00:00:00 UTC)\n"
                f"# RH: relative humidity, %\n"
                f"# T: temperature, C\n"
                f"#\n"
                f"# time  RH  T\n"
            )

    def record(self, humidity, temperature, when=None):
        """
        Record new values of humidity & temperature.

        Create new file and path as needed.

        PARAMETERS

        humidity
            *float* :
            Relative humidity, %.
        temperature
            *float* :
            Temperature, C.
        when
            *obj* :
            `datetime.datetime` of these values.
            (default: now)
        """
        dt = when or datetime.datetime.now()
        fname = self.get_daily_file(dt)
        if not os.path.exists(fname):
            self.create_file(fname)
        with open(fname, "a") as f:
            f.write(
                f"{dt.timestamp():.02f}"
                f" {humidity:.01f}"
                f" {temperature:.01f}\n"
            )


if __name__ == "__main__":
    dl = DataLogger("ioc:")
    # when = None
    when = datetime.datetime.fromtimestamp(405783400)
    fname = dl.get_daily_file(when)

    dl.record(50, 25, when)
    dl.record(50.98765, 25.12345)
    time.sleep(2)
    dl.record(50, 25)
    print(fname)
