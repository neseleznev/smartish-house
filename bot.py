#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import re

import telebot
from telebot import types

from core.acestream import start_playback
from core.remote_control import VLC
from core.torrent_server import start_torrent_server, get_url_for_file
from utils import get_token, get_torrent_directory

CONFIG_FILE = 'config.ini'
TOKEN = get_token(CONFIG_FILE)
TORRENT_DIR = get_torrent_directory(CONFIG_FILE)

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"], func=lambda x: True)
def hello_world(message):
    print(message.text)
    today = datetime.datetime.now().strftime('%Y%m%d')

    bot.send_message(
        message.chat.id,
        'Hi, username! Today is '+str(today))


remote = VLC()

MINUS_5_MIN = 'minus5min'
MINUS_15_SEC = 'minus15sec'
PAUSE = 'pause'
PLUS_15_SEC = 'plus15sec'
PLUS_5_MIN = 'plus5min'
FULLSCREEN = 'fullscreen'
VOLUME_UP = 'volume_up'
VOLUME_DOWN = 'volume_down'


@bot.message_handler(content_types=["document"],
                     func=lambda message: message.document.file_name.split('.')[-1] == 'torrent')
def receive_torrent(message):
    file_name, file_id = message.document.file_name, message.document.file_id
    file_path = bot.get_file(file_id).file_path
    file = bot.download_file(file_path)

    # Rename the file to safe alphanumeric
    safe_name = datetime.datetime.now().strftime('%H-%M-%S') + re.sub(r"[^A-Za-z0-9_\s.]", '', file_name)

    with open(os.path.join(TORRENT_DIR, safe_name), 'wb') as f:
        f.write(file)

    start_torrent_server(TORRENT_DIR)
    start_playback(get_url_for_file(safe_name))

    reply_markup = types.InlineKeyboardMarkup()
    # btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='https://example.ru')
    # switch_button = types.InlineKeyboardButton(text='Share something', switch_inline_query="Telegram")
    # reply_markup.add(btn_my_site)
    # reply_markup.add(switch_button)

    reply_markup.row(
        telebot.types.InlineKeyboardButton('⏪5 min', callback_data='remote-' + MINUS_5_MIN),
        telebot.types.InlineKeyboardButton('⏪15 sec', callback_data='remote-' + MINUS_15_SEC),
        telebot.types.InlineKeyboardButton('⏯', callback_data='remote-' + PAUSE),
        telebot.types.InlineKeyboardButton('15 sec⏩', callback_data='remote-' + PLUS_15_SEC),
        telebot.types.InlineKeyboardButton('5 min⏩', callback_data='remote-' + PLUS_5_MIN)
    ).row(
        telebot.types.InlineKeyboardButton('Fullscreen', callback_data='remote-' + FULLSCREEN),
        telebot.types.InlineKeyboardButton('⏹', callback_data='torrent-stop'),
        telebot.types.InlineKeyboardButton('🎵➕', callback_data='remote-' + VOLUME_UP),
        telebot.types.InlineKeyboardButton('🎵➖', callback_data='remote-' + VOLUME_DOWN)
    )

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

    print(action)
    import time
    time.sleep(5)
    if action == MINUS_5_MIN:
        remote.seek('-5M')
    if action == MINUS_15_SEC:
        remote.seek('-15S')
    if action == PAUSE:
        remote.pause()
    if action == PLUS_15_SEC:
        remote.seek('+15S')
    if action == PLUS_5_MIN:
        remote.seek('+5M')
    if action == FULLSCREEN:
        remote.fullscreen()
    if action == VOLUME_UP:
        remote.volume('+15')
    if action == VOLUME_DOWN:
        remote.volume('-15')


if __name__ == '__main__':
    bot.polling(none_stop=True)
