#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser


def get_token(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename)
    try:
        return config['DEFAULT']['token']
    except KeyError:
        warn_missing_config(config_filename)


def get_torrent_directory(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename)
    try:
        return config['DEFAULT']['torrent_dir']
    except KeyError:
        warn_missing_config(config_filename)


def warn_missing_config(config_filename):
    print("""Please, provide %s file with the following content:
            [DEFAULT]
            token: xxxxxxx:12345678901234567890
        """.format(config_filename))
