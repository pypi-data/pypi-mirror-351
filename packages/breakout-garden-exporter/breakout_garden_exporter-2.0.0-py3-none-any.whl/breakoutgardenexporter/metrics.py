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

from typing import Dict, List

HELP_FORMAT = "#HELP %s %s"
TYPE_FORMAT = "#TYPE %s %s "
METRIC_FORMAT = "%s{%s} %f"


class MetricType:
    def __init__(self, metric_type) -> None:
        self.type = metric_type

    def __str__(self) -> str:
        return self.type


COUNTER = MetricType("counter")
GAUGE = MetricType("gauge")


class Metric:
    def __init__(self,
                 metric_name: str,
                 metric_type: MetricType,
                 help_text: str) -> None:
        self.metric_name = metric_name
        self.metric_type = metric_type
        self.help_text = help_text
        self.values: Dict[str, float] = {}

    def set(self, tags: str, value: float) -> None:
        self.values[tags] = value

    def clear(self, tags: str) -> None:
        try:
            del self.values[tags]
        except KeyError:
            pass

    def __str__(self) -> str:
        r: List[str] = []
        for tags, value in self.values.items():
            r.append(HELP_FORMAT % (self.metric_name, self.help_text))
            r.append(TYPE_FORMAT % (self.metric_name, self.metric_type))
            r.append(METRIC_FORMAT % (self.metric_name, tags, value))
        return "\n".join(r)


class Metrics:
    def __init__(self) -> None:
        self.metrics: Dict[str, Metric] = {}

    def add_metric(self,
                   metric_name: str,
                   metric_type: MetricType,
                   help_text: str) -> None:
        self.metrics[metric_name] = Metric(metric_name, metric_type, help_text)

    def set(self, metric_name: str, tags: str, value: float) -> None:
        self.metrics[metric_name].set(tags, value)

    def clear(self, metric_name: str, tags: str) -> None:
        try:
            self.metrics[metric_name].clear(tags)
        except KeyError:
            pass

    def __str__(self) -> str:
        return "\n".join(map(str, self.metrics.values()))
