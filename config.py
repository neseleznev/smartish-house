#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import sys

from core.common import Platform


class Config:
    def __init__(self, config_filename):
        self.config = configparser.ConfigParser()
        self.config.read(config_filename)
        self.config_filename = config_filename

    def get_token(self):
        return self._get_property('token')

    def get_torrent_directory(self):
        return self._get_property('torrent_dir')

    def get_platform(self):
        platform = self._get_property('platform')
        if platform == 'ARM_V7':
            return Platform.ARM_V7
        elif platform == 'LINUX_X86':
            return Platform.LINUX_X86

    def _get_property(self, property_name):
        try:
            return self.config['DEFAULT'][property_name]
        except KeyError:
            self._warn_missing_config()
            sys.exit(1)

    def _warn_missing_config(self):
        print("""Please, provide %s file with the following content:
                [DEFAULT]
                token: xxxxxxx:12345678901234567890
                torrent_dir: /path/to/dir
                platform: ARM_V7 # or LINUX_X86
            """.format(self.config_filename))
