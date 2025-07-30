#!/usr/bin/env python3
# breakout-garden-exporter
# Copyright (C) 2024 Andrew Wilkinson
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

try:
    import board  # type: ignore
except NotImplementedError:
    # This allows to run tests on a non-Raspberry Pi platform
    class board:  # type: ignore
        SCL = 0
        SDA = 0
import busio  # type: ignore
from adafruit_pm25.i2c import PM25_I2C  # type: ignore

from .metrics import Metrics, GAUGE
from .sensor import Sensor


class PM25Sensor(Sensor):
    def __init__(self) -> None:
        self.sensor: Optional[PM25_I2C] = None

        self.last_read = 0

    def initialise(self, metrics: Metrics) -> bool:
        try:
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

            self.sensor = PM25_I2C(i2c, None)
        except (RuntimeError, OSError):
            return False
        else:
            metrics.add_metric("bge_airqual_standard",
                               GAUGE,
                               "Air Quality counts in standardized units")
            metrics.add_metric("bge_airqual_environmental",
                               GAUGE,
                               "Air Quality counts in environmental units")
            metrics.add_metric("bge_airqual_particles",
                               GAUGE,
                               "Air Quality particle counts per 1L of air")

            return True

    def measure(self, metrics: Metrics) -> float:
        assert self.sensor is not None, \
            "initialise must be called before measure."

        try:
            aqdata = self.sensor.read()
        except RuntimeError:
            self.last_read += 1
            if self.last_read > 120:
                for psize in [("1.0", "10"), ("2.5", "25"), ("10.0", "100")]:
                    metrics.clear("bge_airqual_standard",
                                  f"sensor=\"pm25\",psize=\"{psize[0]}\"")
                    metrics.clear("bge_airqual_environmental",
                                  f"sensor=\"pm25\",psize=\"{psize[0]}\"")

                for psize in [("0.3", "03"), ("0.5", "05"), ("1.0", "10"),
                              ("2.5", "25"), ("5.0", "50"), ("10.0", "100")]:
                    metrics.clear("bge_airqual_particles",
                                  f"sensor=\"pm25\",psize=\"{psize[0]}um\"")

            return 1.0

        self.last_read = 0

        for psize in [("1.0", "10"), ("2.5", "25"), ("10.0", "100")]:
            metrics.set("bge_airqual_standard",
                        f"sensor=\"pm25\",psize=\"{psize[0]}\"",
                        aqdata[f"pm{psize[1]} standard"])
            metrics.set("bge_airqual_environmental",
                        f"sensor=\"pm25\",psize=\"{psize[0]}\"",
                        aqdata[f"pm{psize[1]} env"])

        for psize in [("0.3", "03"), ("0.5", "05"), ("1.0", "10"),
                      ("2.5", "25"), ("5.0", "50"), ("10.0", "100")]:
            metrics.set("bge_airqual_particles",
                        f"sensor=\"pm25\",psize=\"{psize[0]}um\"",
                        aqdata[f"particles {psize[1]}um"]*10)

        return 1.0
