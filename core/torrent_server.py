#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import re
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import os
from threading import Thread

import logging

from constants import TORRENT_SERVER_PORT
from core.common import Singleton

log = logging.getLogger(__name__)


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)


class TorrentServer(metaclass=Singleton):

    def __init__(self, directory, port=TORRENT_SERVER_PORT):
        self.directory = directory
        self.port = port
        Thread(
            target=lambda: self.run_torrent_server(),
            name='Torrent Server',
            daemon=True
        ).start()

    def run_torrent_server(self):
        httpd = HTTPServer(self.directory, ("", self.port))
        log.info('Serving Torrents library on port %d', self.port)
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()

    @staticmethod
    def _sanitize_filename(filename):
        # Rename the file to safe alphanumeric
        return datetime.datetime.now().strftime('%H-%M-%S') + re.sub(r"[^A-Za-z0-9_\s.]", '', filename)

    def get_url(self, filename):
        return 'http://localhost:' + str(self.port) + '/' + TorrentServer._sanitize_filename(filename)

    def add(self, file, filename):
        safe_name = TorrentServer._sanitize_filename(filename)

        with open(os.path.join(self.directory, safe_name), 'wb') as f:
            f.write(file)
