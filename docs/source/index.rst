.. dhtioc documentation master file, created by
   sphinx-quickstart on Mon Aug 10 10:31:09 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

dhtioc
======

Provide humidity and temperature using EPICS and Raspberry Pi

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   install
   parts
   code/*
   changes

.. figure:: _static/DHT22-connected-to-zerow.jpg
   :width: 40%

   Assembled *dhtioc* system.

Typical measurements from *dhtioc* plotted:

.. figure:: _static/2020-11-daily-porch.png
    :width: 80%

    Readings from *dhtioc* system mounted on front porch.
    Values recorded every few seconds, logged into files.
    Note the unseasonably warm temperatures until Nov. 10.
    Definitely rainy on Nov. 14-15.  Also, some rain on Nov. 10.


References
-------------

* `Balena Etcher <https://www.balena.io/etcher/>`_
* `caproto <https://github.com/caproto/caproto>`_
* `EPICS <https://epics.anl.gov/>`_
* `RPi CircuitPython <https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi>`_
* `RPi pinout <https://pinout.xyz/>`_
* `RPi OS downloads - <https://www.raspberrypi.org/downloads/>`_
* `RPi WiFi - <https://desertbot.io/blog/headless-raspberry-pi-4-ssh-wifi-setup>`_
* `Statistics - Linear Regression <https://stattrek.com/AP-Statistics-1/Regression.aspx?Tutorial=Stat>`_
* `Statistics - Correlation and Rgression <https://en.ppt-online.org/186857>`_
* `Statistics - numpy polyfit <https://data36.com/linear-regression-in-python-numpy-polyfit>`_
* `Statistics - Weighted least squares<https://en.wikipedia.org/wiki/Weighted_least_squares>`_
* `Statistics - weighted linear regression <http://www.real-statistics.com/multiple-regression/weighted-linear-regression>`_
* `Statistics - least squares method <http://www.real-statistics.com/regression/least-squares-method/>`_
* `Statistics - regression analysis <http://www.real-statistics.com/regression/regression-analysis/>`_
* `Statistics - Deming regression <http://www.real-statistics.com/regression/deming-regression/deming-regression-basic-concepts/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
