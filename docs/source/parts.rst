.. _partslist:

Parts, Purchasing
=================

* RPi Zero W, preferred for *this* project:

  * RPi Zero series, because it easily runs headless,
    and only needs a 5 VDC, 1A power supply with micro USB connector.
  * Unlike the plain RPi Zero, has built-in WiFi.
  * Unlike the RPi Zero WH, you can solder just the pins you
    want, so you don't expose **possible short circuits** of supply
    Voltage to ground from the unused pins.

    .. figure:: _static/exposed-pins.jpg
       :width: 40%

       Exposed pins when a full GPIO header is soldered
       to the RPi Zero board.

.. index:: NextCloudPi

* RPi 4 running `NextCloudPi <https://raspberrytips.com/install-nextcloud-raspberry-pi/>`_ :
  Follow the wiring and installation instructions to add *dhtioc* to
  your NextCloudPi server!

.. tip:: Enclosures

   .. index:: enclosure

   For the best measurement of ambient conditions, place the DHT22
   sensor head *outside* of the enclosure. Place the sensor *inside* to
   measure the RPi operating temperature.


Parts List
----------

1. Raspberry Pi (any model)

   1. power supply for the RPi (if you don't have)
   2. SD card for the RPi, 4GB or larger (if you don't have)

   3. enclosure or case for the RPi (**suggested**, optional)

.. index:: DHT22

2. DHT22 (AM2302) Digital Humidity & Temperature sensor

   1. solderable header pins, sockets, jumper wires (optional), as needed
   2. connector wiring (optional), as needed


Purchasing Suggestions
----------------------

* RPi Zero W complete starter kit:
   https://www.microcenter.com/product/627789/vilros-raspberry-pi-zero-w-complete-starter-kit

* RPi Zero W kit:
   https://www.microcenter.com/product/606952/canakit-raspberry-pi-zero-w-(wireless)-with-official-case-and-power-supply

* RPi Zero W board:
   https://www.adafruit.com/category/933?src=raspberrypi

.. index:: enclosure; indoor

* Adafruit case for the Zero:
  https://www.adafruit.com/product/3252
  *or*
  https://chicagodist.com/products/adafruit-raspberry-pi-zero-case

  .. figure:: _static/adafruit-enclosure.jpg
      :width: 40%

      Adafruit enclosure with RPi Zero W for indoors.

.. index:: enclosure; outdoor

* outdoor electrical outlet enclosure:
  https://www.homedepot.com/p/Red-Dot-1-Gang-GFCI-Weatherproof-Non-Metallic-Electrical-Box-Cover-Kit-S355P/204193191

  .. figure:: _static/outdoor-enclosure.jpg
      :width: 40%

      Outdoor enclosure with RPi Zero W.

.. index:: DHT22

* DHT22 sensor:
  https://www.amazon.com/HiLetgo-Temperature-Humidity-Electronic-Practice/dp/B0795F19W6

  .. figure:: _static/DHT22.jpg
        :width: 40%

        DHT22 sensor, with supplied jumper wiring.

* header pins & sockets, assortment:
  https://www.amazon.com/MCIGICM-Connector-Assortment-arduino-Stackable/dp/B07X23LQQF
  *or*
  https://chicagodist.com/search?q=header

* jumper wires: pin/pin, socket/socket:
  https://www.adafruit.com/category/306
  *or*
  https://chicagodist.com/search?q=jumper%20wire
