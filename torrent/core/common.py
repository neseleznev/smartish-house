#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Platform:
    ARM_V7 = 0
    LINUX_X86 = 1
    # WINDOWS = 2
