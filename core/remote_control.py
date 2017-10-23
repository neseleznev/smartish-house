import json
import urllib.request
from urllib.error import URLError

import telebot

from core.common import Singleton


class VLC(metaclass=Singleton):
    MINUS_5_MIN = 'minus5min'
    MINUS_15_SEC = 'minus15sec'
    PAUSE = 'pause'
    PLUS_15_SEC = 'plus15sec'
    PLUS_5_MIN = 'plus5min'
    FULLSCREEN = 'fullscreen'
    VOLUME_UP = 'volume_up'
    VOLUME_DOWN = 'volume_down'

    def __init__(self, port):
        self.port = port
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.
        password_mgr.add_password(None, self.api_root, '', 'pass')
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        self.opener = urllib.request.build_opener(handler)

    @property
    def api_root(self):
        return 'http://127.0.0.1:' + str(self.port) + '/requests/'

    @property
    def api_command(self):
        return self.api_root + 'status.json?command='

    def open(self, url):
        try:
            self.opener.open(url)
        except URLError as ex:
            print(ex)

    def fullscreen(self):
        self.open(self.api_command + 'fullscreen')

    # interval could be +1M -1M +5S -5S, etc.
    def seek(self, interval: str):
        self.open(self.api_command + 'seek&val=' + interval)

    def pause(self):
        self.open(self.api_command + 'pl_pause')

    def stop(self):
        self.open(self.api_command + 'pl_stop')

    # interval could be +5 -5 30%, etc.
    def volume(self, interval: str):
        self.open(self.api_command + 'volume&val=' + interval)

    def add_control_rows(self, reply_markup, prefix):
        reply_markup.row(
            telebot.types.InlineKeyboardButton('⏪5 min', callback_data=prefix + self.MINUS_5_MIN),
            telebot.types.InlineKeyboardButton('⏪15 sec', callback_data=prefix + self.MINUS_15_SEC),
            telebot.types.InlineKeyboardButton('⏯', callback_data=prefix + self.PAUSE),
            telebot.types.InlineKeyboardButton('15 sec⏩', callback_data=prefix + self.PLUS_15_SEC),
            telebot.types.InlineKeyboardButton('5 min⏩', callback_data=prefix + self.PLUS_5_MIN)
        ).row(
            telebot.types.InlineKeyboardButton('Fullscreen', callback_data=prefix + self.FULLSCREEN),
            telebot.types.InlineKeyboardButton('🎵➕', callback_data=prefix + self.VOLUME_UP),
            telebot.types.InlineKeyboardButton('🎵➖', callback_data=prefix + self.VOLUME_DOWN)
        )
        return reply_markup

    def control(self, action):
        if action == self.MINUS_5_MIN:
            self.seek('-5M')
        if action == self.MINUS_15_SEC:
            self.seek('-15S')
        if action == self.PAUSE:
            self.pause()
        if action == self.PLUS_15_SEC:
            self.seek('+15S')
        if action == self.PLUS_5_MIN:
            self.seek('+5M')
        if action == self.FULLSCREEN:
            self.fullscreen()
        if action == self.VOLUME_UP:
            self.volume('+15')
        if action == self.VOLUME_DOWN:
            self.volume('-15')


class Kodi(metaclass=Singleton):
    MINUS_5_MIN = 'minus5min'
    MINUS_15_SEC = 'minus15sec'
    PAUSE = 'pause'
    PLUS_15_SEC = 'plus15sec'
    PLUS_5_MIN = 'plus5min'
    NEXT_AUDIO = 'next_audio'
    NEXT_SUBS = 'next_subs'
    VOLUME_UP = 'volume_up'
    VOLUME_DOWN = 'volume_down'

    def __init__(self, port):
        self.port = port
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        # Add the username and password.
        # If we knew the realm, we could use it instead of None.
        password_mgr.add_password(None, self.api_root, 'kodi', 'kodi')
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        self.opener = urllib.request.build_opener(handler)

    @property
    def api_root(self):
        return 'http://127.0.0.1:' + str(self.port) + '/jsonrpc'

    def api_method(self, method, params):
        return self.api_root + '?request={"jsonrpc":"2.0","id":1,"method":"' + method + '","params":' + params + '}'

    def open(self, url):
        try:
            print(url)
            return self.opener.open(url)
        except URLError as ex:
            print(ex)

    def get_player_id(self):
        json_response = self.open(self.api_method('Player.GetActivePlayers', '{}')).read().decode('utf-8')
        response = json.loads(json_response)
        for el in response["result"]:
            if el["type"] == "video":
                return str(el["playerid"])

    # interval description http://kodi.wiki/view/JSON-RPC_API/v8#Player.Seek
    def seek(self, interval: str):
        player_id = self.get_player_id()
        if not player_id:
            print('Nothing is playing!')
            return
        self.open(self.api_method('Player.Seek', '{"playerid":' + player_id + ',"value":"' + interval + '"}'))

    def pause(self):
        player_id = self.get_player_id()
        if not player_id:
            print('Nothing is playing!')
            return
        self.open(self.api_method('Player.PlayPause', '{"playerid":' + player_id + '}'))

    # FIXME not working
    def next_audio_source(self):
        player_id = self.get_player_id()
        if not player_id:
            print('Nothing is playing!')
            return
        self.open(self.api_method('Player.SetAudioStream', '{"playerid":' + player_id + ',"stream":"next"}'))

    # FIXME not working
    def next_subtitle(self):
        player_id = self.get_player_id()
        if not player_id:
            print('Nothing is playing!')
            return
        self.open(self.api_method('Player.SetSubtitle', '{"playerid":' + player_id + ',"subtitle":"next"}'))

    # # interval could be "increment", "decrement", and number
    def volume(self, value):
        v = '"{}"'.format(value) if value else '{}'.format(value)
        self.open(self.api_method('Application.SetVolume', '{"volume":' + v + '}'))

    def add_control_rows(self, reply_markup, prefix):
        reply_markup.row(
            telebot.types.InlineKeyboardButton('⏪10 min', callback_data=prefix + self.MINUS_5_MIN),
            telebot.types.InlineKeyboardButton('⏪30 sec', callback_data=prefix + self.MINUS_15_SEC),
            telebot.types.InlineKeyboardButton('⏯', callback_data=prefix + self.PAUSE),
            telebot.types.InlineKeyboardButton('30 sec⏩', callback_data=prefix + self.PLUS_15_SEC),
            telebot.types.InlineKeyboardButton('10 min⏩', callback_data=prefix + self.PLUS_5_MIN)
        ).row(
            telebot.types.InlineKeyboardButton('🇬🇧📢', callback_data=prefix + self.NEXT_AUDIO),
            telebot.types.InlineKeyboardButton('🇬🇧📖', callback_data=prefix + self.NEXT_SUBS),
            telebot.types.InlineKeyboardButton('🎵➕', callback_data=prefix + self.VOLUME_UP),
            telebot.types.InlineKeyboardButton('🎵➖', callback_data=prefix + self.VOLUME_DOWN)
        )
        return reply_markup

    def control(self, action):
        if action == self.MINUS_5_MIN:
            self.seek('bigbackward')
        if action == self.MINUS_15_SEC:
            self.seek('smallbackward')
        if action == self.PAUSE:
            self.pause()
        if action == self.PLUS_15_SEC:
            self.seek('smallforward')
        if action == self.PLUS_5_MIN:
            self.seek('bigforward')
        if action == self.NEXT_AUDIO:
            self.next_audio_source()
        if action == self.NEXT_SUBS:
            self.next_subtitle()
        if action == self.VOLUME_UP:
            self.volume('increment')
        if action == self.VOLUME_DOWN:
            self.volume('decrement')
