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

from breakoutgardenexporter import PM25Sensor, Metrics

import breakoutgardenexporter.pm25

# Needed to fix tests in GitHub actions.
if not hasattr(breakoutgardenexporter.pm25.board, "SCL"):
    breakoutgardenexporter.pm25.board.SCL = 0
if not hasattr(breakoutgardenexporter.pm25.board, "SDA"):
    breakoutgardenexporter.pm25.board.SDA = 0

SAMPLE_DATA = {'pm10 standard': 2,
               'pm25 standard': 3,
               'pm100 standard': 4,
               'pm10 env': 2,
               'pm25 env': 3,
               'pm100 env': 4,
               'particles 03um': 678,
               'particles 05um': 188,
               'particles 10um': 22,
               'particles 25um': 2,
               'particles 50um': 0,
               'particles 100um': 0}


class TestPM25(unittest.TestCase):
    @patch("breakoutgardenexporter.pm25.PM25_I2C")
    @patch("breakoutgardenexporter.pm25.busio.I2C")
    def test_create_sensor(self, mock_busio, mock_pm25):
        instance = Mock()
        mock_pm25.return_value = instance
        instance.read.return_value = SAMPLE_DATA

        metrics = Metrics()
        sensor = PM25Sensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertIn("bge_airqual_standard{sensor=\"pm25\",psize=\"1.0\"} 2",
                      str(metrics))
        self.assertIn("bge_airqual_environmental{sensor=\"pm25\","
                      + "psize=\"2.5\"} 3",
                      str(metrics))
        self.assertIn("bge_airqual_particles{sensor=\"pm25\","
                      + "psize=\"0.3um\"} 6780",
                      str(metrics))

    @patch("breakoutgardenexporter.pm25.busio.I2C")
    @patch("breakoutgardenexporter.pm25.PM25_I2C")
    def test_false_when_no_sensor(self, mock_pm25, mock_busio):
        mock_pm25.side_effect = RuntimeError()

        metrics = Metrics()
        sensor = PM25Sensor()

        self.assertFalse(sensor.initialise(metrics))
