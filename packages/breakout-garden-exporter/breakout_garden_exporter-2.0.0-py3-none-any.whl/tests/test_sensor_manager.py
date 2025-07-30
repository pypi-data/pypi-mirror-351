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

from typing import cast, Optional
import unittest
from unittest.mock import patch, Mock

from breakoutgardenexporter import sensor, sensor_manager, Metrics, COUNTER


class MockSensor(sensor.Sensor):
    def __init__(self) -> None:
        self.counter = 0
        self.manager: Optional[sensor_manager.SensorManager] = None

    def initialise(self, metrics: Metrics) -> bool:
        metrics.add_metric("test_metric", COUNTER, "help_text")
        return True

    def measure(self, metrics: Metrics) -> float:
        self.counter += 1
        metrics.set("test_metric", "", self.counter)
        if self.counter >= 2 and self.manager is not None:
            self.manager.terminate = True
        return 1.0


class TestSensorManager(unittest.TestCase):
    def setUp(self):
        self.old_sensors = sensor_manager.SENSORS
        sensor_manager.SENSORS = [MockSensor]

    def tearDown(self) -> None:
        sensor_manager.SENSORS = self.old_sensors
        return super().tearDown()

    @patch("breakoutgardenexporter.sensor_manager.time")
    def test_one_second_sensor(self, mock_time):
        mock_time.time.side_effect = [1, 2, 3]

        metrics = Mock()
        manager = sensor_manager.SensorManager(metrics)
        cast(MockSensor, list(manager.sensors.keys())[0]).manager = manager
        manager.run()

        metrics.set.assert_called_with("test_metric", "", 2)
        mock_time.sleep.assert_called_with(1.0)
