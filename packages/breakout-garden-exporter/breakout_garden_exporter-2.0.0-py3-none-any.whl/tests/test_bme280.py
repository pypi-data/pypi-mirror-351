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

from breakoutgardenexporter import BME280Sensor, Metrics


class TestBME280(unittest.TestCase):
    @patch("breakoutgardenexporter.bme280.BME280")
    @patch("breakoutgardenexporter.bme280.SMBus")
    def test_create_sensor(self, mock_smbus, mock_bme280):
        instance = Mock()
        mock_bme280.return_value = instance
        instance.get_temperature.return_value = 20.0
        instance.get_pressure.return_value = 1000
        instance.get_humidity.return_value = 65

        metrics = Metrics()
        sensor = BME280Sensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertIn(
            "bge_pressure{sensor=\"bme280\"} 1000.000000", str(metrics))
        self.assertIn(
            "bge_temperature{sensor=\"bme280\"} 20.000000", str(metrics))
        self.assertIn(
            "bge_humidity{sensor=\"bme280\"} 65.000000", str(metrics))

    @patch("breakoutgardenexporter.bme280.BME280")
    @patch("breakoutgardenexporter.bme280.SMBus")
    def test_missing_sensor(self, mock_bme280, mock_smbus):
        instance = Mock()
        mock_bme280.side_effect = RuntimeError

        metrics = Metrics()
        sensor = BME280Sensor()

        self.assertFalse(sensor.initialise(metrics))
