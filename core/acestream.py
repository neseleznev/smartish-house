#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acestream Launcher: Open acestream links with any media player

http://wiki.acestream.org/wiki/index.php/Engine_API
Inspired by https://github.com/jonian/acestream-launcher/blob/master/acestream_launcher.py
"""

import json
import os
import re
import sys
import time
import hashlib
import urllib.request
from subprocess import PIPE
from threading import Thread
from urllib.error import URLError

import psutil
import pexpect

from constants import VLC_PORT, TORRENT_SERVER_PORT, KODI_PORT
from core.common import Platform


class AceStreamEngine(object):
    """Acestream Launcher"""

    def __init__(self, platform, options):
        self.platform = platform

        """Set up engine params"""
        if self.platform == Platform.LINUX_X86:
            self.engine_log = os.path.join(
                os.path.dirname(os.path.realpath(sys.argv[0])),
                'log',
                'acestream.log')
            self.engine_args = ['acestreamengine', '--client-console', '--log-file', self.engine_log]
        elif self.platform == Platform.ARM_V7:
            self.engine_log = '/opt/acestream/acestream.log'
            self.engine_args = ['/opt/acestream/start_acestream.sh']
        else:
            raise NotImplementedError(self.platform + ' is not currently supported')

        """Set up players"""
        if platform == Platform.LINUX_X86:  # or platform == Platform.WINDOWS:
            self.player_args = ['vlc', '--extraintf', 'http',
                                '--http-host=127.0.0.1',
                                '--http-port='+str(options.get('vlc_port', VLC_PORT)),
                                '--http-password=pass']
        elif platform == Platform.ARM_V7:
            if not AceStreamEngine._is_process_running('kodi', '/usr/bin/'):
                psutil.Popen('kodi')
            self.kodi_port = str(options.get('kodi_port', KODI_PORT))
            print('Started Kodi. JSON-RPC API on port', self.kodi_port)
        # elif platform == ugly ARM_V7:
        #     self.player_args = ['omxplayer', '-p', '-o', 'local', '--win', "'0 0 1280 800'"]

        """Set up notifications"""
        if platform == Platform.LINUX_X86:
            import notify2
            from dbus.exceptions import DBusException

            self.app_name = 'AceStream Launcher'
            try:
                notify2.init(self.app_name)
                self.notifier = notify2.Notification(self.app_name)
                self.is_notify_available = True
            except DBusException:
                self.is_notify_available = False
        else:
            self.is_notify_available = False

        self.kill_running_engine()
        self.start_acestream()

    @staticmethod
    def _get_port():
        import os
        # Windows
        if os.name == 'nt':
            port_file = os.path.join(os.getenv('APPDATA'), r'ACEStream\engine', 'acestream.port')
            if not os.path.isfile(port_file):
                raise FileNotFoundError('Unable to get AceStream port number from file ' + port_file)
            with open(port_file) as f:
                return f.readline()
        else:
             return '62062'

    def notify(self, message):
        """Show player status notifications"""

        messages = {
            'running': 'Started AceStream Engine on port ' + self._get_port(),
            'waiting': 'Waiting for channel response...',
            'started': 'Streaming started. Launching player.',
            'noauth': 'Error authenticating to Acestream!',
            'noengine': 'Acstream engine not found in provided path!',
            'unavailable': 'Acestream channel unavailable!',
            'kodi': 'Kodi is not responding'
        }
        print(messages.get(message, message))

        if self.is_notify_available:
            icon = self.player_args[0]
            self.notifier.update(self.app_name, messages.get(message, message), icon)
            self.notifier.show()

    def kill_running_engine(self):
        if self.platform == Platform.LINUX_X86:
            for process in psutil.process_iter():
                if 'acestreamengine' in process.name():
                    process.kill()
        elif self.platform == Platform.ARM_V7:
            try:
                psutil.Popen('/opt/acestream/stop_acestream.sh', stdout=PIPE)
            except FileNotFoundError:
                pass
        time.sleep(10)
        self.notify('Killed all running AceStream Engine instances (+10 seconds)')

    def start_acestream(self):
        """Starts detached acestream process with logs redirected"""

        try:
            psutil.Popen(self.engine_args)
        except FileNotFoundError:
            self.notify('noengine')
            self.destroy(1)

        # Read redirected output
        self.acestream = psutil.Popen('sudo su -', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.acestream.stdin.write(('tail -n 0 -f ' + self.engine_log + '\n').encode('utf-8'))
        self.acestream.stdin.flush()

        lines = []
        for line in self.acestream.stdout:
            line = line.decode('utf-8')
            lines.append(line)
            if 'KILL' in line:
                self.notify(''.join(lines[-5:]))
                self.destroy(1)
            if 'ready to receive remote commands' in line:
                self.notify('running')
                break

    @staticmethod
    def _is_process_running(process_name, process_path='/'):
        ps = psutil.Popen("ps -eaf | grep " + process_name, shell=True, stdout=PIPE)
        output = ps.stdout.read()
        ps.stdout.close()
        ps.wait()
        output = output.decode('utf-8')
        if re.search(process_path + process_name, output) is None:
            return False
        return True

    # noinspection PyMethodParameters
    def acestream_running(func):
        """
        Ensures that AceStream Engine is running and starts it if needed,
        accordingly to a self.platform"""

        def wrapper(*args):
            self = args[0]

            if self.platform == Platform.LINUX_X86:
                is_running = AceStreamEngine._is_process_running('acestreamengine')
            elif self.platform == Platform.ARM_V7:
                is_running = AceStreamEngine._is_process_running('start_acestream.sh', '/opt/acestream/')
            else:
                raise NotImplementedError(self.platform + ' is not currently supported')

            if not is_running:
                self.start_acestream()

            # noinspection PyCallingNonCallable
            return func(*args)
        return wrapper

    # noinspection PyArgumentList
    @acestream_running
    def play_torrent(self, torrent):
        errors = []
        for _ in range(3):
            try:
                self._start_session(torrent)
            except ValueError as e:
                errors.append(e)
                if len(errors) == 3:
                    self.notify('Three errors in a row ' + '\n'.join(errors))
                    # self.destroy(1)
            else:
                break

        url = self._get_playback_url()
        self._open_stream_url(url)

    def _start_session(self, torrent):
        """Start acestream telnet session"""

        product_key = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'

        session = pexpect.spawn('telnet 127.0.0.1 ' + self._get_port())

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
            raise ValueError('noauth')

        try:
            session.timeout = 30

            torrent = torrent.replace('localhost', '127.0.0.1', 1)
            print(torrent)
            session.sendline('LOADASYNC 467763 TORRENT '+torrent+' 0 0 0')
            session.expect('LOADRESP 467763 {.*}')
            json_response = '{' + session.after.decode('utf-8').split('{')[1]
            response = json.loads(json_response)
            print(response)
            infohash = response['infohash']
            checksum = response['checksum']

            session.sendline('GETCID infohash='+infohash+' checksum='+checksum+' developer=0 affiliate=0 zone=0')
            session.expect('##.*')
            self.cid = session.after.decode('utf-8').split('##')[1].rstrip()

            session.sendline('START TORRENT '+torrent+' 0 0 0 0')
            session.expect('http://.*')

            self.session = session
            # self.url = session.after.decode('utf-8').split()[0]

            self.notify('started')
        except (pexpect.TIMEOUT, pexpect.EOF):
            self.notify('unavailable')
            # self.destroy(1)
            self.kill_running_engine()
        except KeyError:
            raise ValueError('unavailable')

    def _get_playback_url(self):
        """Start the media player"""

        lines = []
        for line in self.acestream.stdout:
            print(line.decode('utf-8'))
            lines.append(line.decode('utf-8'))
            if 'STOP' in line.decode('utf-8'):
                self.notify(''.join(lines[-5:]))
                self.kill_running_engine()
            if 'START http://127.' in line.decode('utf-8'):
                return line.decode('utf-8').split('START ')[1].rstrip()

    def _open_stream_url(self, url):
        if self.platform == Platform.LINUX_X86:
            self.player_args.append(url)
            self.player = psutil.Popen(self.player_args)
            self.player.wait()
            self.session.sendline('STOP')
            self.session.sendline('SHUTDOWN')

        elif self.platform == Platform.ARM_V7:
            api_root = 'http://127.0.0.1:' + self.kodi_port + '/jsonrpc'
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, api_root, 'kodi', 'kodi')
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            try:
                request_url = (api_root +
                               '?request={%22jsonrpc%22:%222.0%22,'
                               '%22id%22:1,'
                               '%22method%22:%22Player.Open%22,'
                               '%22params%22:{%22item%22:{%22file%22:%22' + url + '%22}}}')
                print('Sending GET ' + request_url)
                response = opener.open(request_url)
                print(response.read().decode('utf-8'))
            except URLError as ex:
                print(ex)
                self.notify('kodi')
                self.kill_running_engine()

    def destroy(self, code=0):
        """Close acestream and media player"""

        if self.platform == Platform.LINUX_X86:
            try:
                self.player.kill()
            except (AttributeError, psutil.NoSuchProcess):
                print('Media Player not running...')

            try:
                self.acestream.kill()
            except (AttributeError, psutil.NoSuchProcess):
                print('Acestream not running...')

        sys.exit(code)

    def _run_playback(self, torrent_url):
        """Start Acestream Launcher"""

        try:
            self.play_torrent(torrent_url)
        except (KeyboardInterrupt, EOFError):
            self.notify('Acestream Launcher exiting...')
            self.kill_running_engine()
            sys.exit(0)

    def start_playback(self, torrent_url):
        Thread(
            target=lambda: self._run_playback(torrent_url),
            name='AceStream Engine and VLC Player'
        ).start()

if __name__ == '__main__':
    engine = AceStreamEngine(Platform.LINUX_X86, {'vlc_port': VLC_PORT})
    engine.play_torrent('http://127.0.0.1:' + TORRENT_SERVER_PORT + '/07-28-06_The_Fountain__.torrent')
