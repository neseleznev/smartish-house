#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

import telebot
from telebot import types

from core.acestream import AceStreamEngine
from core.common import Platform
from core.remote_control import VLC
from core.torrent_server import TorrentServer
from utils import get_token, get_torrent_directory, get_platform

CONFIG_FILE = 'config.ini'
TORRENT_SERVER_PORT = 8880
KODI_PORT = 8080
VLC_PORT = 8881

TOKEN = get_token(CONFIG_FILE)
TORRENT_DIR = get_torrent_directory(CONFIG_FILE)
PLATFORM = get_platform(CONFIG_FILE)

torrents = TorrentServer(TORRENT_DIR, TORRENT_SERVER_PORT)
engine = AceStreamEngine(Platform.ARM_V7, {'kodi_port': KODI_PORT})
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"], func=lambda x: True)
def hello_world(message):
    print(message.text)
    today = datetime.datetime.now().strftime('%Y%m%d')

    bot.send_message(
        message.chat.id,
        'Hi, username! Today is '+str(today))


remote = VLC()



@bot.message_handler(content_types=["document"],
                     func=lambda message: message.document.file_name.split('.')[-1] == 'torrent')
def receive_torrent(message):
    filename, file_id = message.document.file_name, message.document.file_id
    file_path = bot.get_file(file_id).file_path
    file = bot.download_file(file_path)

    torrents.add(file, filename)

    engine.start_playback(torrents.get_url(filename))

    reply_markup = types.InlineKeyboardMarkup()
    # btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='https://example.ru')
    # switch_button = types.InlineKeyboardButton(text='Share something', switch_inline_query="Telegram")
    # reply_markup.add(btn_my_site)
    # reply_markup.add(switch_button)

    reply_markup = remote.add_control_rows(reply_markup)

    bot.send_message(message.chat.id, 'Your remote control', reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('remote-'):
        remote_control(query)
    if data == 'torrent-stop':
        print('Terminate acestream, clean cache, terminate vlc, hide keyboard')


def remote_control(query):
    bot.answer_callback_query(query.id)
    action = query.data.split('remote-')[1]
    bot.send_chat_action(query.message.chat.id, 'typing')
    remote.control(action)

if __name__ == '__main__':
    bot.polling(none_stop=True)
