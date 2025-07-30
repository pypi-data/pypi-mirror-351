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

from icp10125 import ICP10125

from .metrics import Metrics, GAUGE
from .sensor import Sensor


class ICP10125Sensor(Sensor):
    def __init__(self) -> None:
        self.sensor: Optional[ICP10125] = None

    def initialise(self, metrics: Metrics) -> bool:
        try:
            self.sensor = ICP10125()
        except (RuntimeError, OSError):
            return False
        else:
            metrics.add_metric("bge_pressure", GAUGE, "The air pressure")
            metrics.add_metric("bge_temperature", GAUGE, "The temperature")

            return True

    def measure(self, metrics: Metrics) -> float:
        assert self.sensor is not None, \
            "initialise must be called before measure."
        pressure, temperature = self.sensor.measure()
        if pressure > 10000:
            pressure /= 100

        metrics.set("bge_pressure", "sensor=\"icp10125\"", pressure)
        metrics.set("bge_temperature", "sensor=\"icp10125\"", temperature)

        return 1.0
