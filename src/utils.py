#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from logging import warning, error


# Define application icon
def set_icon(entry_icon=None):
    icon = '/usr/share/pixmaps/whats.svg'
    l_icon = '../appdata/whats.svg'

    if entry_icon is not None:
        icon = '/usr/share/whats/icon_status/' + entry_icon + '.png'
        l_icon = '../icon_status/' + entry_icon + '.png'

    try:
        with open(icon):
            return icon
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        try:
            with open(l_icon):
                return l_icon
        except Exception as msg:
            # Exception for icon not found
            error('\033[31m %s \033[m', msg)
            return None
