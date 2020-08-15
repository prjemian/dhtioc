Installation
============

Prepare a Raspberry Pi (RPi) to read a DHT22 (digital humidity and
temperature sensor) and post values as an EPICS IOC server.

1. Initial configuration of the RPi
1. Installation of required libraries
1. Installation of the project code
1. Run the project

Initial Configuration
*********************

There are several steps to configure a new RaspberryPi for use.
We'll follow (more or less) this guide from Adafruit:
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

1. Connect a DHT22 sensor to the RPi
1. Prepare the Operating System media
1. Boot the RPi
1. Pick a unique host name
1. ``raspi-config``
1. Apply Operating system updates
1. Enable the hardware interfaces used by this project
1. Make *Python v3* be the default ``python``
1. Reboot

Connect the DHT22 sensor
------------------------

TODO: pictures

1. solder pin headers (for RPi Zero-W)
1. connect DHT signal (center pin) to RPi pin 4 (as shown)

Prepare the Operating System media
----------------------------------

1. OS Media choice: micro SD card, 4 GB (larger is not needed for this project but works fine, takes longer to flash AND backup, takes more space to backup)
1. flash a new Raspberry Pi OS Lite onto a micro SD card (Balena Etcher recommended)
1. enable SSH login: create empty ``ssh`` file on `boot` partition
1. configure WiFi: create ``wpa_supplicant.conf`` file on `boot` partition per https://desertbot.io/blog/headless-raspberry-pi-4-ssh-wifi-setup
1. Make *Python v3* be the default `python` (python v2 is EOL starting 2020).

* https://www.raspberrypi.org/downloads/
* https://www.balena.io/etcher/

Boot the RPi
------------

1. install micro SD card in RPi and apply power
1. identify new RPi IP number on your subnet and login: ``ssh pi@new.I.P.number``
1. password is ``raspberry`` until you change it (highly recommended)

Pick a unique host name
-----------------------

If you plan on having more than one RPi on your local subnet,
then you should give a unique to each and every one of them.  You can
be creative, or mundane.  Here, we name our pi based on its Serial
number (from ``/proc/cpuinfo``).  We'll start with ``rpi`` (to make the
host name recognizable), then pick the last four characters
of the serial number, expecting that to make a unique name::

    echo "Suggested host name: rpi$(cat /proc/cpuinfo  | grep Serial | tail -c 5)"

Use this name in ``raspi-config`` below.

raspi-config
------------

Run ``sudo raspi-config`` and configure these settings:

* 1 change password for user ``pi``
* 2 Network Options: N1 Hostname -- pick a unique name, see suggestion above
* 4 Localisation Options: I2 Change Timezone -- (if not set in ``wpa_supplicant.conf`` file)
* 5 Interfacing Options: P4 SPI -- **Yes**
* 5 Interfacing Options: P5 I2C -- **Yes**
* 5 Interfacing Options: P8 Remote GPIO -- **No**
* 8 Update -- select it

You may be prompted to reboot now.  Probably best to reboot if you changed the hostname.

In different versions of RaspberryPi OS and ``raspi-config``, these
settings may be moved to other submenus.  You might have to hunt for them.

Apply Operating system updates
------------------------------

Update the operating system with latest changes, patches, and security items.
This command only runs the install if the first command (identify the
packages with available upgrades) succeeds::

    sudo apt-get update && sudo apt-get upgrade -y

This step could take some time (5-60 or more), depending on how
many updates have been released since your download of the OS image
was released.

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
    sudo ln -f -s $(which python3) /etc/alternatives/python
    sudo ln -f -s /etc/alternatives/python /usr/bin/python
    # or this interactive method
    #   sudo update-alternatives --config python

Reboot
------

Finally, after all these steps, reboot the RPi.  ``sudo reboot``

Installation of required libraries
**********************************

Enable the _I2C_ and _SPI_ interfaces::

    sudo apt-get install -y python3-smbus i2c-tools

This command will show any I2C or SPI devices in the system::

    ls -l /dev/{i2c,spi}*

Any i2c-connected devices will report their address here::

    sudo i2cdetect -y 1

::

    # install python modules to support our Python code
    # need module adafruit_dht
    # https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    pip3 install RPI.GPIO adafruit-blinka adafruit-circuitpython-dht
    sudo apt-get install -y libgpiod2

    # need module caproto
    pip3 install caproto  --no-warn-script-location

Installation of the project code
********************************

::

    mkdir ~/Documents
    cd ~/Documents
    git clone https://github.com/prjemian/dhtioc
    cd dhtioc/dhtioc/

Run the project
***************

::

    ./sensor.py -h
    ./sensor.py --list-pvs --prefix ${HOSTNAME}:
