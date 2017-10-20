#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import re

import telebot

from core.acestream import start_playback
from core.torrent_server import start_torrent_server, get_url_for_file
from utils import get_token, get_torrent_directory

CONFIG_FILE = 'config.ini'
TOKEN = get_token(CONFIG_FILE)
TORRENT_DIR = get_torrent_directory(CONFIG_FILE)

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"], func=lambda x: True)
def hello_world(message):
    today = datetime.datetime.now().strftime('%Y%m%d')

    bot.send_message(
        message.chat.id,
        'Hi, username! Today is '+str(today))


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
    # start_playback(get_url_for_file(safe_name))


if __name__ == '__main__':
    bot.polling(none_stop=True)
