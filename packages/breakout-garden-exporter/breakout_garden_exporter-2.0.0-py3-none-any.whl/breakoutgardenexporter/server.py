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
import http.server
import socketserver
from typing import cast, Any, Callable

from .metrics import Metrics


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, metrics: Metrics, quiet=False) -> None:
        self.metrics = metrics
        self.quiet = quiet

    def __call__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_index()
        elif self.path == "/metrics":
            self.send_metrics()
        else:
            self.send_error(404)

    def send_index(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write("""
<html>
<head><title>Breakout Garden Exporter</title></head>
<body>
<h1>Breakout Garden Exporter</h1>
<p><a href="/metrics">Metrics</a></p>
</body>
</html>""".encode("utf8"))

    def send_metrics(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str(self.metrics).encode("utf8"))

    def log_request(self, code='-', size='-') -> None:
        if self.quiet:
            return
        else:
            self.log_message('"%s" %s %s',
                             self.requestline, str(code), str(size))


def serve(metrics: Metrics,
          args: argparse.Namespace) -> None:  # pragma: no cover
    handler = cast(Callable[[Any, Any, http.server.HTTPServer],
                            socketserver.BaseRequestHandler],
                   Handler(metrics, args.quiet))
    server = http.server.HTTPServer(args.bind, handler)
    server.serve_forever()
