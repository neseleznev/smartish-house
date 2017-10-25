#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import logging
import sys

from torrent.core import Platform

log = logging.getLogger(__name__)

DEFAULT_SECTION_ERROR = """Please, provide %s file with the following content:
    [DEFAULT]
    token: xxxxxxx:12345678901234567890
"""
TORRENT_SECTION_ERROR = """Please, provide %s file with the following content:
    [TORRENT]
    dir: /path/to/dir
    platform: ARM_V7 or LINUX_X86
"""
SERVER_SECTION_ERROR = """Please, make sure your SERVER section contains
following or remove it at all to use long-polling:
    [SERVER]
    host: 12.34.56.78 or domain.com
    key: server/webhook_pkey.key
    cert: server/webhook_cert.pem
"""


class Config:
    def __init__(self, config_filename):
        self.config = configparser.ConfigParser()
        self.config.read(config_filename)
        self.config_filename = config_filename

    def get_token(self):
        return self._get_property('DEFAULT', 'token')

    def get_torrent_directory(self):
        return self._get_property('TORRENT', 'dir')

    def get_platform(self):
        platform = self._get_property('TORRENT', 'platform')
        if platform == 'ARM_V7':
            return Platform.ARM_V7
        elif platform == 'LINUX_X86':
            return Platform.LINUX_X86

    def get_webhook_settings(self):
        try:
            telegram = self.config['SERVER']
            assert 'host' in telegram
            assert 'key' in telegram
            assert 'cert' in telegram
            return telegram
        except KeyError:
            return None
        except AssertionError:
            log.error(SERVER_SECTION_ERROR)
            sys.exit(1)

    def _get_property(self, section, property_name):
        try:
            return self.config[section][property_name]
        except KeyError:
            if section == 'DEFAULT':
                log.error(DEFAULT_SECTION_ERROR.format(self.config_filename))
            elif section == 'TORRENT':
                log.error(TORRENT_SECTION_ERROR.format(self.config_filename))
            sys.exit(1)
