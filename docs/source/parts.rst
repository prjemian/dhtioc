.. _partslist:

Parts, Connections, Purchasing
==============================

* RPi Zero W, preferred for *this* project:

   * RPi Zero series, because it easily runs headless,
     and only needs a 5 VDC, 1A power supply with
     micro USB connector.
   * Unlike the plain RPi Zero, has built-in WiFi.
   * Unlike the RPi Zero WH, you can solder just the pins you
      want, so you don't expose possible short circuits of
      supply Voltage to ground from the unused pins.

* RPi 4 running `NextCloudPi <https://raspberrytips.com/install-nextcloud-raspberry-pi/>`_ :
   Follow the wiring and installation instructions to
   add *dhtioc* to your NextCloudPi server!

Parts List
----------

1. Raspberry Pi (any model)

   1. power supply for the RPi (if you don't have)
   2. SD card for the RPi, 4GB or larger (if you don't have)

   3. enclosure or case for the RPi (optional)

2. DHT22 (AM2302) Digital Humidity & Temperature sensor

   1. solderable header pins, sockets, jumper wires (optional), as needed
   2. connector wiring (optional), as needed


Connections
-----------

1. Solder a 6-pin socket header to the Zero W board,
   covering `GPIO pins 1,3,5,7,9,11 <https://pinout.xyz>`_

2. Press a 5-pin strip of right-angle header pins into
   the sockets for pins 1,3,5,7,9

3. connect the 3 pins of the DHT22 as follows:

   =========   ========  ==========
   DHT22 pin   GPIO pin  meaning
   =========   ========  ==========
   ``+``       1         *3v3 Power* (+3.3 VDC)
   ``out``     7         *GPIO 4* (to match the software)
   ``-``       9         *Ground*
   =========   ========  ==========

Purchasing Suggestions
----------------------

* RPi Zero W complete starter kit:
   https://www.microcenter.com/product/627789/vilros-raspberry-pi-zero-w-complete-starter-kit

* RPi Zero W kit:
   https://www.microcenter.com/product/606952/canakit-raspberry-pi-zero-w-(wireless)-with-official-case-and-power-supply

* RPi Zero W board:
   https://www.adafruit.com/category/933?src=raspberrypi

* Adafruit case for the Zero:
  https://www.adafruit.com/product/3252

* outdoor electrical outlet cover:
  https://www.homedepot.com/p/Red-Dot-1-Gang-GFCI-Weatherproof-Non-Metallic-Electrical-Box-Cover-Kit-S355P/204193191

* DHT22 sensor:
  https://www.amazon.com/HiLetgo-Temperature-Humidity-Electronic-Practice/dp/B0795F19W6

* header pins & sockets, assortment:
  https://www.amazon.com/MCIGICM-Connector-Assortment-arduino-Stackable/dp/B07X23LQQF

* jumper wires: pin/pin, socket/socket:
  https://www.adafruit.com/category/306
