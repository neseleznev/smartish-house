#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acestream Launcher: Open acestream links with any media player

http://wiki.acestream.org/wiki/index.php/Engine_API
Inspired by https://github.com/jonian/acestream-launcher/blob/master/acestream_launcher.py
"""

import json
import sys
import time
import hashlib
# import argparse
from subprocess import PIPE
from threading import Thread

import psutil
import pexpect
import notify2

VLC_SERVER_PORT = 8081


class AceStreamEngine(object):
    """Acestream Launcher"""

    def __init__(self, torrent_url):
        self.torrent = torrent_url
        self.engine_args = ['acestreamengine', '--client-console']
        self.player_args = ['vlc', '--extraintf', 'http',
                            '--http-host=127.0.0.1',
                            '--http-port='+str(VLC_SERVER_PORT),
                            '--http-password=pass']
        # For Windows
        # self.player_args = ['vlc', '--extraintf http', '--http-host=127.0.0.1', '--http-port=8081', '--http-password=pass']
    #     parser = argparse.ArgumentParser(
    #         prog='acestream-launcher',
    #         description='Open acestream links with any media player'
    #     )
    #     parser.add_argument(
    #         'url',
    #         metavar='URL',
    #         help='the acestream url to play'
    #     )
    #     parser.add_argument(
    #         '-e', '--engine',
    #         help='the engine command to use (default: acestreamengine --client-console)',
    #         default='acestreamengine --client-console'
    #     )
    #     parser.add_argument(
    #         '-p', '--player',
    #         help='the media player command to use (default: vlc)',
    #         default='vlc'
    #     )
        self.appname = 'Acestream Launcher'
        # self.args = parser.parse_args()

        notify2.init(self.appname)
        self.notifier = notify2.Notification(self.appname)

        self.start_acestream()
        self.start_session()
        self.start_player()
        self.close_player()

    def notify(self, message):
        """Show player status notifications"""

        icon = self.player_args[0]
        messages = {
            'running': 'Acestream engine running.',
            'waiting': 'Waiting for channel response...',
            'started': 'Streaming started. Launching player.',
            'noauth': 'Error authenticating to Acestream!',
            'noengine': 'Acstream engine not found in provided path!',
            'unavailable': 'Acestream channel unavailable!'
        }

        print(messages[message])
        self.notifier.update(self.appname, messages[message], icon)
        self.notifier.show()

    def start_acestream(self):
        """Start acestream engine"""

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.kill()

        try:
            self.acestream = psutil.Popen(self.engine_args, stdout=PIPE)
            self.notify('running')
            time.sleep(5)
        except FileNotFoundError:
            self.notify('noengine')
            self.close_player(1)

    @staticmethod
    def get_port():
        import os
        # Linux
        if os.name == 'posix':
            return 62062

        # Windows
        if os.name == 'nt':
            port_file = os.path.join(os.getenv('APPDATA'), r'ACEStream\engine', 'acestream.port')
            if not os.path.isfile(port_file):
                raise FileNotFoundError('Unable to get AceStream port number from file ' + port_file)

            with open(port_file) as f:
                return int(f.readline())

    def start_session(self):
        """Start acestream telnet session"""

        product_key = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'

        session = pexpect.spawn('telnet localhost '+str(self.get_port()))

        try:
            session.timeout = 1000
            session.sendline('HELLOBG version=3')
            session.expect('key=.*')

            request_key = session.after.decode('utf-8').split()[0].split('=')[1]
            signature = (request_key + product_key).encode('utf-8')
            signature = hashlib.sha1(signature).hexdigest()
            response_key = product_key.split('-')[0] + '-' + signature
            # pid = self.args.url.split('://')[1]

            session.sendline('READY key=' + response_key)
            session.expect('AUTH.*')
            # session.sendline('USERDATA [{"gender": "1"}, {"age": "3"}]')

            self.notify('waiting')
        except (pexpect.TIMEOUT, pexpect.EOF):
            self.notify('noauth')
            self.close_player(1)

        try:
            session.timeout = 30

            session.sendline('LOADASYNC 467763 TORRENT '+self.torrent+' 0 0 0')
            session.expect('LOADRESP 467763 {.*}')
            json_response = '{' + session.after.decode('utf-8').split('{')[1]
            response = json.loads(json_response)
            infohash = response['infohash']
            checksum = response['checksum']

            session.sendline('GETCID infohash='+infohash+' checksum='+checksum+' developer=0 affiliate=0 zone=0')
            session.expect('##.*')
            self.cid = session.after.decode('utf-8').split('##')[1].rstrip()

            session.sendline('START TORRENT '+self.torrent+' 0 0 0 0')
            session.expect('http://.*')

            self.session = session
            # self.url = session.after.decode('utf-8').split()[0]

            self.notify('started')
        except (pexpect.TIMEOUT, pexpect.EOF):
            self.notify('unavailable')
            self.close_player(1)

    def start_player(self):
        """Start the media player"""

        url = None

        # time.sleep(10)
        lines = []
        for line in self.acestream.stdout:
            print(line.decode('utf-8'))
            lines.append(line.decode('utf-8'))
            if 'STOP' in line.decode('utf-8'):
                raise BaseException(''.join(lines[-5:]))
            if 'START http://127.' in line.decode('utf-8'):
                url = line.decode('utf-8').split('START ')[1].rstrip()
                break

        self.player_args.append(url)

        self.player = psutil.Popen(self.player_args)
        self.player.wait()
        self.session.sendline('STOP')
        self.session.sendline('SHUTDOWN')

    def close_player(self, code=0):
        """Close acestream and media player"""

        try:
            self.player.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Media Player not running...')

        try:
            self.acestream.kill()
        except (AttributeError, psutil.NoSuchProcess):
            print('Acestream not running...')

        sys.exit(code)


def run_torrent_in_vlc(torrent_url):
    """Start Acestream Launcher"""

    try:
        AceStreamEngine(torrent_url)
    except (KeyboardInterrupt, EOFError):
        print('Acestream Launcher exiting...')

        for process in psutil.process_iter():
            if 'acestreamengine' in process.name():
                process.kill()

        sys.exit(0)


def start_playback(torrent_url):
    Thread(
        target=lambda: run_torrent_in_vlc(torrent_url),
        name='AceStream Engine and VLC Player'
    ).start()


if __name__ == '__main__':
    run_torrent_in_vlc('http://localhost:8080/07-28-06_The_Fountain__.torrent')
