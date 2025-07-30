#!/usr/bin/env python3
# breakout-garden-exporter
# Copyright (C) 2023 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from smbus2 import SMBus
try:
    from bme280 import BME280
except OSError:
    pass

from .metrics import Metrics, GAUGE
from .sensor import Sensor


class BME280Sensor(Sensor):
    def __init__(self) -> None:
        self.sensor: Optional[BME280] = None

    def initialise(self, metrics: Metrics) -> bool:
        try:
            self.sensor = BME280(i2c_dev=SMBus(1))
            self.sensor.setup()
        except RuntimeError:
            return False
        else:
            metrics.add_metric("bge_pressure", GAUGE, "The air pressure")
            metrics.add_metric("bge_temperature", GAUGE, "The temperature")
            metrics.add_metric("bge_humidity", GAUGE, "The humidity")

            return True

    def measure(self, metrics: Metrics) -> float:
        assert self.sensor is not None, \
            "initialise must be called before measure."

        temperature = self.sensor.get_temperature()
        pressure = self.sensor.get_pressure()
        humidity = self.sensor.get_humidity()
        print(temperature, pressure, humidity)

        metrics.set("bge_temperature",
                    "sensor=\"bme280\"",
                    temperature)
        metrics.set("bge_pressure",
                    "sensor=\"bme280\"",
                    pressure)
        metrics.set("bge_humidity",
                    "sensor=\"bme280\"",
                    humidity)

        return 1.0
