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

from breakoutgardenexporter import SGP30Sensor, Metrics


class MockSGP30Reading:
    def __init__(self, co2, voc) -> None:
        self.equivalent_co2 = co2
        self.total_voc = voc


class TestSGP30(unittest.TestCase):
    @patch("breakoutgardenexporter.sgp30.SGP30")
    def test_create_sensor(self, mock_sgp30):
        instance = Mock()
        mock_sgp30.return_value = instance
        instance.get_air_quality.side_effect = \
            [MockSGP30Reading(400, 0), MockSGP30Reading(405, 5)]

        metrics = Metrics()
        sensor = SGP30Sensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertIn(
            "bge_equivalent_co2{sensor=\"sgp30\"} 405.000000", str(metrics))
        self.assertIn(
            "bge_voc{sensor=\"sgp30\"} 5.000000", str(metrics))

    @patch("breakoutgardenexporter.sgp30.SGP30")
    def test_missing_sensor(self, mock_sgp30):
        instance = Mock()
        mock_sgp30.side_effect = OSError

        metrics = Metrics()
        sensor = SGP30Sensor()

        self.assertFalse(sensor.initialise(metrics))
