#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser

from core.common import Platform


def get_token(config_filename):
    return get_property(config_filename, 'token')


def get_torrent_directory(config_filename):
    return get_property(config_filename, 'torrent_dir')


def get_platform(config_filename):
    platform = get_property(config_filename, 'platform')
    if platform == 'ARM_V7':
        return Platform.ARM_V7
    elif platform == 'LINUX_X86':
        return Platform.LINUX_X86


def get_property(config_filename, property):
    config = configparser.ConfigParser()
    config.read(config_filename)
    try:
        return config['DEFAULT'][property]
    except KeyError:
        warn_missing_config(config_filename)


def warn_missing_config(config_filename):
    print("""Please, provide %s file with the following content:
            [DEFAULT]
            token: xxxxxxx:12345678901234567890
            torrent_dir: /path/to/dir
            platform: ARM_V7 # or LINUX_X86
        """.format(config_filename))
