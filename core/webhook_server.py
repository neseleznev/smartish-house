# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.key 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST
from http.server import BaseHTTPRequestHandler

import telebot


# WebhookHandler, process webhook calls
# noinspection PyPep8Naming
class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "WebhookHandler/1.0"
    bot = None
    url_path = None

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == self.url_path and \
                        'content-type' in self.headers and \
                        'content-length' in self.headers and \
                        self.headers['content-type'] == 'application/json':
            json_string = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')

            self.send_response(200)
            self.end_headers()

            update = telebot.types.Update.de_json(json_string)
            self.bot.process_new_messages([update.message])
        else:
            self.send_error(403)
            self.end_headers()
