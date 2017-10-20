#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import os
from threading import Thread

TORRENT_SERVER_PORT = 8080


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


def run_torrent_server(directory):
    httpd = HTTPServer(directory, ("", TORRENT_SERVER_PORT))
    # httpd.serve_forever()
    print("serving torrents at port", TORRENT_SERVER_PORT)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


def start_torrent_server(directory):
    Thread(
        target=lambda: run_torrent_server(directory),
        name='Torrent Server',
        daemon=True
    ).start()


def get_url_for_file(filename):
    return 'http://localhost:' + str(TORRENT_SERVER_PORT) + '/' + filename
