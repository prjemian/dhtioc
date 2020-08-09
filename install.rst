Installation
============

1. initial configuration
1. Initial configuration of the RPi
1. Installation of required libraries
1. Installation of the project code
1. Run the project

Initial Configuration
*********************

There are several steps to configure a new RaspberryPi for use.

1. Connect a DHT22 sensor to the RPi
1. Prepare the Operating System media
1. Boot the RPi
1. ``raspi-config``
1. Apply Operating system updates
1. Enable the hardware interfaces used by this project
1. Make *Python v3* be the default ``python``
1. Change the host name
1. Reboot

Connect the DHT22 sensor
------------------------

TODO: pictures

1. solder pin headers (for RPi Zero-W)
1. connect DHT signal (center pin) to RPi pin 4 (as shown)

Prepare the Operating System media
----------------------------------

1. OS Media choice: micro SD card, 4 GB (larger is not needed for this project but works fine)
1. flash a new RaspberryPi OS Lite onto a micro SD card (Balena Etcher recommended)
1. enable SSH login: create empty ``ssh`` file on `boot` partition
1. configure WiFi: create ``wpa_supplicant.conf`` file on `boot` partition per https://desertbot.io/blog/headless-raspberry-pi-4-ssh-wifi-setup
1. Enable the hardware interfaces used by this project
1. Make *Python v3* be the default `python` (python v2 is EOL starting 2020).

Boot the RPi
------------

1. install micro SD card in RPi and apply power
1. identify new RPi IP number on your subnet and login: ``ssh pi@new.I.P.number``
1. password is ``raspberry`` until you change it (highly recommended)

raspi-config
------------

Run ``sudo raspi-config`` and configure these settings:

* 1 change password for user ``pi``
* 3 Localisation Options: I2 Change Timezone -- (if not set in ``wpa_supplicant.conf`` file)
* 4 Interfacing Options: P4 SPI -- **Yes**
* 4 Interfacing Options: P5 I2C -- **Yes**
* 4 Interfacing Options: P8 Remote GPIO -- **No**
* 8 Update -- select it

Apply Operating system updates
------------------------------

Update the operating system with latest changes, patches, and security items.
This command only runs the install if the first command (identify the
packages with available upgrades) succeeds::

    sudo apt-get update && sudo apt-get upgrade -y

Enable the hardware interfaces used by this project
---------------------------------------------------

Enable the _I2C_ and _SPI_ interfaces::

    sudo apt-get install -y python3-smbus i2c-tools

.. TODO: How to enable loading of I2C kernel module from command line?
   # see: https://www.instructables.com/id/How-to-enable-I2C-on-RaspberryPI/ (both I2C & SPI)

After a reboot, this command will show any I2C or SPI devices in the system::

    ls -l /dev/{i2c,spi}*

After a reboot, any i2c-connected devices will report their address here::

    sudo i2cdetect -y 1

Make *Python v3* be the default ``python``
------------------------------------------

By default, python v2 is what you get when you type ``python``.
Since python v2 reached the end-of-life after 2019, we want ``python3``
to be called when we type ``python``.  Here's how to make that happen:

    # make python3 the default python
    sudo apt-get install -y python3 git python3-pip
    sudo pip3 install --upgrade setuptools
    sudo update-alternatives --install /usr/bin/python python $(which python2) 1
    sudo update-alternatives --install /usr/bin/python python $(which python3) 2
    # TODO: next line requires a keyboard response -- Is there an alternative?
    # --config asks the user for response.  Is this step needed or is default already made?
    sudo update-alternatives --config python

Change the host name
--------------------

If you plan on having more than one RaspberryPi on your local subnet,
then you should give a unique to each and every one of them.  You can
be creative, or mundane.  Here, we name our pi based on its Serial
number (from ``/proc/cpuinfo``).  We'll start with ``rpi`` (to make the
host name recognizable), then pick the last four characters
of the serial number, expecting that to make a unique name::

    export hn=$(cat /proc/cpuinfo  | grep Serial | tail -c 5)
    sudo hostname rpi${hn}

This takes effect right away (confirm with command: ``hostname``)
**BUT** the ``HOSTNAME`` environment variable is not updated until the
next reboot.  But we can do that now::

    export HOSTNAME=$(hostname)

Reboot
------

Finally, after all these steps, reboot the RPi.

Installation of required libraries
**********************************

::

    # install python modules to support our Python code
    # need module adafruit_dht
    # https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    pip3 install RPI.GPIO adafruit-blinka
    # do NOT install this package!
    # NO # pip3 install adafruit-circuitpython-dht
    # sudo apt-get install -y libgpiod2
    # see: https://github.com/prjemian/rpi_dht22/issues/12
    # instead:
    pip3 install Adafruit_DHT

    # need module caproto
    pip3 install caproto  --no-warn-script-location

Installation of the project code
********************************

::

    mkdir ~/Documents
    cd ~/Documents
    git clone https://github.com/prjemian/rpi_dht22
    cd rpi_dht22/rpi_dht22_epics/

Run the project
***************

::

    ./sensor.py -h
    ./sensor.py --list-pvs --prefix ${HOSTNAME}:
