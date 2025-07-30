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

import time
import threading
from typing import Dict

from .bme280 import BME280Sensor
from .icp10125 import ICP10125Sensor
from .metrics import Metrics
from .pm25 import PM25Sensor
from .sensor import Sensor
from .sgp30 import SGP30Sensor

SENSORS = [BME280Sensor, ICP10125Sensor, PM25Sensor, SGP30Sensor]


class SensorManager(threading.Thread):
    def __init__(self, metrics: Metrics) -> None:
        threading.Thread.__init__(self)
        self.daemon = True
        self.sensors: Dict[Sensor, float] = {}
        self.metrics = metrics
        self.terminate = False

        for sensor_class in SENSORS:
            sensor = sensor_class()
            if sensor.initialise(self.metrics):
                self.sensors[sensor] = 0

    def run(self) -> None:
        while not self.terminate:
            delay = min(self.sensors.values())

            if delay > 0:
                start = time.time()
                time.sleep(delay)
                slept = time.time() - start

                for key in self.sensors.keys():
                    self.sensors[key] -= slept

            for sensor, sleep in self.sensors.items():
                if sleep <= 0:
                    self.sensors[sensor] = sensor.measure(self.metrics)
