#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging

import telebot
from telebot import types

from constants import VLC_PORT, KODI_PORT, TORRENT_SERVER_PORT
from core.acestream import AceStreamEngine
from core.common import Platform
from core.remote_control import VLC, Kodi
from core.torrent_server import TorrentServer
from config import Config
from utils import setup_logging

log = logging.getLogger(__name__)
setup_logging(log_directory='log', file_level=logging.DEBUG, console_level=logging.INFO)
log.critical('SALAM')

config = Config('config.ini')
TOKEN = config.get_token()
TORRENT_DIR = config.get_torrent_directory()
PLATFORM = config.get_platform()

if PLATFORM == Platform.LINUX_X86:
    options = {'vlc_port': VLC_PORT}
    remote = VLC(VLC_PORT)
elif PLATFORM == Platform.ARM_V7:
    options = {'kodi_port': KODI_PORT}
    remote = Kodi(KODI_PORT)
else:
    options = dict()

torrents = TorrentServer(TORRENT_DIR, TORRENT_SERVER_PORT)
engine = AceStreamEngine(PLATFORM, options)
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"], func=lambda x: True)
def hello_world(message):
    log.debug('User %s sent a message "%s"', 'username', message.text)
    today = datetime.datetime.now().strftime('%Y%m%d')

    bot.send_message(
        message.chat.id,
        'Hi, username! Today is '+str(today))


@bot.message_handler(content_types=["document"],
                     func=lambda message: message.document.file_name.split('.')[-1] == 'torrent')
def receive_torrent(message):
    filename, file_id = message.document.file_name, message.document.file_id
    file_path = bot.get_file(file_id).file_path
    file = bot.download_file(file_path)
    log.debug('User %s sent a torrent file "%s"', 'username', filename)

    torrents.add(file, filename)
    engine.start_playback(torrents.get_url(filename))

    reply_markup = types.InlineKeyboardMarkup()
    # btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='https://example.ru')
    # switch_button = types.InlineKeyboardButton(text='Share something', switch_inline_query="Telegram")
    # reply_markup.add(btn_my_site)
    # reply_markup.add(switch_button)
    reply_markup = remote.add_control_rows(reply_markup, 'remote-')

    bot.send_message(message.chat.id, 'Your remote control', reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda q: q.data.startswith('remote-'))
def rc_callback(query):
    bot.answer_callback_query(query.id)
    action = query.data.split('remote-')[1]
    bot.send_chat_action(query.message.chat.id, 'typing')
    remote.control(action)


@bot.callback_query_handler(func=lambda q: q.data.startswith('torrent-'))
def torrent_callback(query):
    data = query.data
    if data == 'torrent-stop':
        log.warning('Terminate acestream, clean cache, terminate vlc, hide keyboard')

if __name__ == '__main__':
    bot.polling(none_stop=True)
