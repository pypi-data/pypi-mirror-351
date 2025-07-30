# breakout-garden-exporter

[![Pipeline](https://github.com/andrewjw/breakout-garden-exporter/actions/workflows/build.yml/badge.svg)](https://github.com/andrewjw/breakout-garden-exporter/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/breakout-garden-exporter)](https://pypi.org/project/breakout-garden-exporter/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/glowprom)](https://pypi.org/project/breakout-garden-exporter/)
[![Coverage Status](https://coveralls.io/repos/github/andrewjw/breakout-garden-exporter/badge.svg?branch=main)](https://coveralls.io/github/andrewjw/breakout-garden-exporter?branch=master)

Exposes Prometheus metrics from sensors that are part of [Pimoroni's Breakout Garden family](https://shop.pimoroni.com/collections/breakout-garden).

```
usage: breakout-garden-exporter [-h] [-q] [--bind [BIND]]

Exposes Prometheus metrics from sensors that are part of Pimoroni's Breakout Garden family

optional arguments:
  -h, --help     show this help message and exit
  -q, --quiet    don't log HTTP requests
  --bind [BIND]  the ip address and port to bind to. Default: *:9101
```

Currently supported devices are:

* ICP10125 temperature and pressure sensor (e.g. [this](https://shop.pimoroni.com/products/icp10125-air-pressure-breakout))
* SGP30 CO2 and VOC air quality sensors (e.g. [this](https://shop.pimoroni.com/products/sgp30-air-quality-sensor-breakout))
* BME280 temperature, pressure and humidity sensor (e.g. [this](https://shop.pimoroni.com/products/bme280-breakout))
* PM25 air quality sensors (e.g. [this](https://shop.pimoroni.com/products/adafruit-pmsa003i-air-quality-breakout-stemma-qt-qwiic) connect via an [appropriate breakout board](https://shop.pimoroni.com/products/breakout-garden-to-qwiic-adaptor?))

If you have any other breakout devices, please get in touch so we can add support for them!
  
