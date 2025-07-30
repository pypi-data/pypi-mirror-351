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

import os
import unittest

from breakoutgardenexporter import get_arguments


class TestArguments(unittest.TestCase):
    def setUp(self):
        os.environ = {}

    def test_bind_without_port(self):
        args = get_arguments(["--bind", "192.168.1.2"])
        self.assertEqual("192.168.1.2", args.bind[0])
        self.assertEqual(9101, args.bind[1])

    def test_bind_with_port(self):
        args = get_arguments(["--bind", "192.168.1.2:9020"])
        self.assertEqual("192.168.1.2", args.bind[0])
        self.assertEqual(9020, args.bind[1])
