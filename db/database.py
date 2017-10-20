#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

from core.common import Singleton


class Database(metaclass=Singleton):
    def __init__(self):
        self.conn = sqlite3.connect('db/sqlite.db')
        self.cursor = self.conn.cursor()

    def execute(self, raw_sql, *args):
        return self.cursor.execute(raw_sql, *args)

    def commit(self):
        self.conn.commit()
