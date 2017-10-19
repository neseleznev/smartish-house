#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

import telebot

from utils import get_token

CONFIG_FILE = 'config.ini'

bot = telebot.TeleBot(get_token(CONFIG_FILE))


@bot.message_handler(content_types=["text"], func=lambda x: True)
def hello_world(message):
    today = datetime.datetime.now().strftime('%Y%m%d')

    bot.send_message(
        message.chat.id,
        f'Hi, {"username"}! Today is {today}')


if __name__ == '__main__':
    bot.polling(none_stop=True)
