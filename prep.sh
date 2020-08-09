#!/bin/bash

# file: prep.sh

# prepare this RPi to read the DHT22 and post values as an EPICS IOC

# set the hostname based on the RPi's serial number, last four characters
export hn=`cat /proc/cpuinfo  | grep Serial | tail -c 5`
sudo hostname rpi${hn}

# TODO: what other localizations usually done through raspi-config?
# I2C, SPI

# Enable I2C and SPI
sudo apt-get install -y python3-smbus i2c-tools
# TODO: How to enable loading of I2C kernel module from command line?
# see: https://www.instructables.com/id/How-to-enable-I2C-on-RaspberryPI/ (both I2C & SPI)
# after a reboot, any i2c-connected devices will report their address here
sudo i2cdetect -y 1
# after a reboot, any I2C or SPI devices will show up here
ls -l /dev/{i2c,spi}*

sudo apt-get update
sudo apt-get upgrade -y

# make python3 the default python
sudo apt-get install -y python3 git python3-pip
sudo pip3 install --upgrade setuptools
sudo update-alternatives --install /usr/bin/python python $(which python2) 1
sudo update-alternatives --install /usr/bin/python python $(which python3) 2
# TODO: next line requires a keyboard response -- Is there an alternative?
# --config asks the user for response.  Is this step needed or is default already made?
sudo update-alternatives --config python

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

mkdir ~/Documents
cd ~/Documents
git clone https://github.com/prjemian/rpi_dht22
cd rpi_dht22/rpi_dht22_epics/
./sensor.py -h
./sensor.py --list-pvs --prefix ${HOSTNAME}:
