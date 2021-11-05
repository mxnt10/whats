#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules
from logging import warning, error
from os import remove
from os.path import expanduser, isfile
from shutil import copy

# Import sources
import jsonTools as j

# Variables for define locals for autostart configuration
orig = '/usr/share/applications/whats.desktop'
dest = expanduser('~/.config/autostart')
desk = dest + '/whats.desktop'


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


# verify if exist the file whats.desktop in auto start folder
def set_desktop():
    try:
        if not isfile(desk) and j.set_json('AutoStart') == 'True':
            with open(orig):
                copy(orig, dest)
        elif isfile(desk) and j.set_json('AutoStart') == 'False':
            remove(desk)
        return True

    except Exception as msg:
        error('\033[31m %s \033[m', msg)
        j.write_json('AutoStart', 'False')
        return False
