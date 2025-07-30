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

from breakoutgardenexporter import ICP10125Sensor, Metrics


class TestICP10125(unittest.TestCase):
    @patch("breakoutgardenexporter.icp10125.ICP10125")
    def test_create_sensor(self, mock_icp10125):
        instance = Mock()
        mock_icp10125.return_value = instance
        instance.measure.return_value = (1001.5, 25.5)

        metrics = Metrics()
        sensor = ICP10125Sensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertIn(
            "bge_pressure{sensor=\"icp10125\"} 1001.500000", str(metrics))
        self.assertIn(
            "bge_temperature{sensor=\"icp10125\"} 25.500000", str(metrics))

    @patch("breakoutgardenexporter.icp10125.ICP10125")
    def test_false_when_no_sensor(self, mock_icp10125):
        mock_icp10125.side_effect = RuntimeError()

        metrics = Metrics()
        sensor = ICP10125Sensor()

        self.assertFalse(sensor.initialise(metrics))
