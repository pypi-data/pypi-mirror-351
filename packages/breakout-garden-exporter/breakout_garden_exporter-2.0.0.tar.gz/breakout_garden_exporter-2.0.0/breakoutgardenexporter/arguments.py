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

import argparse

parser = argparse.ArgumentParser(
    description='Exposes Prometheus metrics from sensors that are part '
                + 'of Pimoroni\'s Breakout Garden family')
parser.add_argument('-q', '--quiet', action="store_true",
                    help="don't log HTTP requests")
parser.add_argument('--bind', type=str, nargs='?', default="0.0.0.0:9101",
                    help='the ip address and port to bind to. Default: *:9101')


def get_arguments(args) -> argparse.Namespace:
    args = parser.parse_args(args)

    if ":" not in args.bind:
        args.bind = (args.bind, 9101)
    else:
        args.bind = (args.bind.split(":")[0], int(args.bind.split(":")[1]))

    return args
