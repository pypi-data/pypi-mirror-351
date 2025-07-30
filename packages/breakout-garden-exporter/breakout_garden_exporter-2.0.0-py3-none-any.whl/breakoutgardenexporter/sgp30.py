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

from sgp30 import SGP30

from .metrics import Metrics, GAUGE
from .sensor import Sensor


class SGP30Sensor(Sensor):
    def __init__(self) -> None:
        self.sensor: Optional[SGP30] = None
        self.warmed_up: bool = False
        self.initial_readings: int = 0

    def initialise(self, metrics: Metrics) -> bool:
        try:
            self.sensor = SGP30()
            self.sensor.command('init_air_quality')
        except OSError:
            return False
        else:
            metrics.add_metric("bge_equivalent_co2",
                               GAUGE,
                               "The equivalent co2 (ppm)")
            metrics.add_metric("bge_voc",
                               GAUGE,
                               "The total VOC (ppb)")

            return True

    def measure(self, metrics: Metrics) -> float:
        assert self.sensor is not None, \
            "initialise must be called before measure."
        result = self.sensor.get_air_quality()

        if result.equivalent_co2 != 400 \
           or result.total_voc != 0 \
           or self.initial_readings >= 20:
            self.warmed_up = True

        if self.warmed_up:
            metrics.set("bge_equivalent_co2",
                        "sensor=\"sgp30\"",
                        result.equivalent_co2)
            metrics.set("bge_voc", "sensor=\"sgp30\"", result.total_voc)
        else:
            self.initial_readings += 1

        return 1.0
